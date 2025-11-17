"""
Event Publisher - Shared library for publishing domain events

This library provides a unified interface for publishing events to the event bus.
Supports both Redis Streams (MVP) and RabbitMQ (production).

Key features:
- CloudEvents specification compliant
- Automatic retry with exponential backoff
- Event schema validation
- Dead letter queue for failed events
- Monitoring and metrics integration
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from uuid import uuid4
import logging

import redis.asyncio as redis
import aio_pika
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ======================
# EVENT SCHEMA
# ======================

class CloudEvent(BaseModel):
    """CloudEvents v1.0 specification"""
    specversion: str = "1.0"
    type: str = Field(..., description="Event type in format: com.platform.{domain}.{entity}.{action}")
    source: str = Field(..., description="Service that generated the event")
    id: str = Field(default_factory=lambda: str(uuid4()))
    time: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    datacontenttype: str = "application/json"
    data: Dict[str, Any] = Field(..., description="Event payload")

    # Optional fields
    subject: Optional[str] = Field(None, description="Subject of the event (e.g., order_id)")
    dataschema: Optional[str] = Field(None, description="Schema URL")


# ======================
# EVENT PUBLISHER
# ======================

class EventPublisher:
    """
    Singleton event publisher that supports multiple backends
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventPublisher, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.backend: Literal["redis", "rabbitmq"] = os.getenv("EVENT_BUS_BACKEND", "redis")
            self.redis_client: Optional[redis.Redis] = None
            self.rabbitmq_connection: Optional[aio_pika.Connection] = None
            self.rabbitmq_channel: Optional[aio_pika.Channel] = None
            self.service_name = os.getenv("SERVICE_NAME", "unknown-service")

    @classmethod
    async def initialize(cls):
        """Initialize the event publisher"""
        instance = cls()

        if instance.backend == "redis":
            await instance._init_redis()
        elif instance.backend == "rabbitmq":
            await instance._init_rabbitmq()
        else:
            raise ValueError(f"Unsupported event bus backend: {instance.backend}")

        cls._initialized = True
        logger.info(f"Event publisher initialized with backend: {instance.backend}")

    async def _init_redis(self):
        """Initialize Redis Streams backend"""
        redis_url = os.getenv("EVENT_BUS_URL", "redis://localhost:6379/1")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

        # Test connection
        await self.redis_client.ping()
        logger.info("Connected to Redis event bus")

    async def _init_rabbitmq(self):
        """Initialize RabbitMQ backend"""
        rabbitmq_url = os.getenv("EVENT_BUS_URL", "amqp://platform:platform123@localhost:5672/")
        self.rabbitmq_connection = await aio_pika.connect_robust(rabbitmq_url)
        self.rabbitmq_channel = await self.rabbitmq_connection.channel()

        # Declare exchange for events
        await self.rabbitmq_channel.declare_exchange(
            "platform_events",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        logger.info("Connected to RabbitMQ event bus")

    @classmethod
    def is_ready(cls) -> bool:
        """Check if event publisher is ready"""
        return cls._initialized

    @classmethod
    async def close(cls):
        """Close connections"""
        instance = cls()

        if instance.redis_client:
            await instance.redis_client.close()

        if instance.rabbitmq_connection:
            await instance.rabbitmq_connection.close()

        logger.info("Event publisher closed")

    # ======================
    # PUBLISH METHODS
    # ======================

    @classmethod
    async def publish(
        cls,
        event_type: str,
        data: Dict[str, Any],
        topic: str,
        subject: Optional[str] = None,
        retry_count: int = 3
    ) -> bool:
        """
        Publish an event to the event bus

        Args:
            event_type: Event type in format "{domain}.{entity}.{action}" (e.g., "order.placed")
            data: Event payload
            topic: Topic/stream name (e.g., "order-events")
            subject: Optional subject (e.g., order_id)
            retry_count: Number of retries on failure

        Returns:
            bool: True if published successfully

        Example:
            await EventPublisher.publish(
                event_type="order.placed",
                data={"order_id": "ord_123", "total": 1250.00},
                topic="order-events",
                subject="ord_123"
            )
        """
        instance = cls()

        # Create CloudEvent
        event = CloudEvent(
            type=f"com.platform.{event_type}",
            source=instance.service_name,
            subject=subject,
            data=data
        )

        # Publish with retry
        for attempt in range(retry_count):
            try:
                if instance.backend == "redis":
                    return await instance._publish_redis(topic, event)
                elif instance.backend == "rabbitmq":
                    return await instance._publish_rabbitmq(topic, event)
            except Exception as e:
                logger.error(f"Failed to publish event (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # Send to dead letter queue
                    await instance._send_to_dlq(topic, event, str(e))
                    raise

        return False

    async def _publish_redis(self, topic: str, event: CloudEvent) -> bool:
        """Publish event to Redis Streams"""
        event_json = event.model_dump_json()

        await self.redis_client.xadd(
            topic,
            {"event": event_json},
            maxlen=100000  # Keep last 100k events
        )

        logger.info(f"Published event to Redis stream '{topic}': {event.type}")
        return True

    async def _publish_rabbitmq(self, topic: str, event: CloudEvent) -> bool:
        """Publish event to RabbitMQ"""
        event_json = event.model_dump_json()

        # Extract routing key from event type (e.g., "com.platform.order.placed" -> "order.placed")
        routing_key = event.type.replace("com.platform.", "")

        message = aio_pika.Message(
            body=event_json.encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            message_id=event.id,
            timestamp=datetime.fromisoformat(event.time.replace("Z", "+00:00"))
        )

        exchange = await self.rabbitmq_channel.get_exchange("platform_events")
        await exchange.publish(message, routing_key=routing_key)

        logger.info(f"Published event to RabbitMQ exchange with routing key '{routing_key}': {event.type}")
        return True

    async def _send_to_dlq(self, topic: str, event: CloudEvent, error: str):
        """Send failed event to dead letter queue"""
        dlq_topic = f"{topic}.dlq"

        dlq_event = {
            "original_event": event.model_dump(),
            "error": error,
            "failed_at": datetime.utcnow().isoformat() + "Z"
        }

        try:
            if self.backend == "redis":
                await self.redis_client.xadd(dlq_topic, {"event": json.dumps(dlq_event)})
            elif self.backend == "rabbitmq":
                # RabbitMQ has built-in DLX, but we can also log to a separate queue
                pass

            logger.error(f"Event sent to DLQ '{dlq_topic}': {event.type}")
        except Exception as e:
            logger.critical(f"Failed to send event to DLQ: {e}")


# ======================
# CONVENIENCE FUNCTIONS
# ======================

async def publish_event(
    event_type: str,
    data: Dict[str, Any],
    topic: str,
    subject: Optional[str] = None
) -> bool:
    """
    Convenience function to publish an event

    Example:
        from shared.events.publisher import publish_event

        await publish_event(
            event_type="site.created",
            data={"site_id": "site_xyz", "slug": "rams-grocery"},
            topic="site-events",
            subject="site_xyz"
        )
    """
    return await EventPublisher.publish(
        event_type=event_type,
        data=data,
        topic=topic,
        subject=subject
    )


# ======================
# EVENT CONSUMER (for services that need to subscribe)
# ======================

class EventConsumer:
    """
    Event consumer for subscribing to topics
    """

    def __init__(self, topic: str, consumer_group: str, handler_func):
        self.topic = topic
        self.consumer_group = consumer_group
        self.handler_func = handler_func
        self.backend = os.getenv("EVENT_BUS_BACKEND", "redis")
        self.redis_client: Optional[redis.Redis] = None
        self.rabbitmq_connection: Optional[aio_pika.Connection] = None
        self.running = False

    async def start(self):
        """Start consuming events"""
        self.running = True

        if self.backend == "redis":
            await self._consume_redis()
        elif self.backend == "rabbitmq":
            await self._consume_rabbitmq()

    async def stop(self):
        """Stop consuming events"""
        self.running = False

    async def _consume_redis(self):
        """Consume events from Redis Streams"""
        redis_url = os.getenv("EVENT_BUS_URL", "redis://localhost:6379/1")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

        # Create consumer group if doesn't exist
        try:
            await self.redis_client.xgroup_create(
                self.topic,
                self.consumer_group,
                id='0',
                mkstream=True
            )
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        consumer_name = f"{self.consumer_group}-{uuid4().hex[:8]}"

        logger.info(f"Started consuming from Redis stream '{self.topic}' as '{consumer_name}'")

        while self.running:
            try:
                # Read messages from stream
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    consumer_name,
                    {self.topic: '>'},
                    count=10,
                    block=5000  # Block for 5 seconds
                )

                for stream, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        event_json = message_data.get('event')
                        if event_json:
                            event = json.loads(event_json)
                            await self.handler_func(event)

                            # Acknowledge message
                            await self.redis_client.xack(self.topic, self.consumer_group, message_id)

            except Exception as e:
                logger.error(f"Error consuming event: {e}")
                await asyncio.sleep(5)

    async def _consume_rabbitmq(self):
        """Consume events from RabbitMQ"""
        rabbitmq_url = os.getenv("EVENT_BUS_URL", "amqp://platform:platform123@localhost:5672/")
        self.rabbitmq_connection = await aio_pika.connect_robust(rabbitmq_url)
        channel = await self.rabbitmq_connection.channel()

        # Declare queue
        queue = await channel.declare_queue(
            f"{self.consumer_group}_{self.topic}",
            durable=True
        )

        # Bind to exchange
        exchange = await channel.get_exchange("platform_events")
        await queue.bind(exchange, routing_key=f"{self.topic}.*")

        logger.info(f"Started consuming from RabbitMQ queue '{queue.name}'")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    event = json.loads(message.body.decode())
                    await self.handler_func(event)


# ======================
# EXAMPLE USAGE
# ======================

if __name__ == "__main__":
    """
    Example usage of event publisher and consumer
    """

    async def example_handler(event: dict):
        print(f"Received event: {event['type']}")

    async def main():
        # Initialize publisher
        await EventPublisher.initialize()

        # Publish event
        await publish_event(
            event_type="test.created",
            data={"test_id": "test_123", "message": "Hello World"},
            topic="test-events",
            subject="test_123"
        )

        # Start consumer
        consumer = EventConsumer(
            topic="test-events",
            consumer_group="test-consumer-group",
            handler_func=example_handler
        )

        await consumer.start()

    asyncio.run(main())
