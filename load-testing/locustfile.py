"""
Load Testing for Multi-Website Platform

Simulates realistic user behavior across different services:
- Browsing products
- Adding to cart
- Checking out
- Booking appointments
- Checking availability

Run with:
    locust -f locustfile.py --host=http://localhost:3000
"""

from locust import HttpUser, task, between, SequentialTaskSet
from faker import Faker
import random
import uuid

fake = Faker()


class StorefrontUserBehavior(SequentialTaskSet):
    """
    Simulates a customer browsing and purchasing from the storefront.
    """

    def on_start(self):
        """Initialize user session."""
        self.site_slug = "demo-store"
        self.site_id = None
        self.cart_id = None
        self.session_id = str(uuid.uuid4())

    @task
    def browse_homepage(self):
        """Visit the homepage."""
        with self.client.get(f"/{self.site_slug}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Homepage failed: {response.status_code}")

    @task
    def browse_products(self):
        """Browse product listing."""
        self.client.get(
            f"http://localhost:8011/api/v1/{self.site_id or 'demo-site'}/products",
            params={"page": 1, "page_size": 20},
            name="/api/products"
        )

    @task
    def view_product_detail(self):
        """View individual product."""
        # Simulate viewing a random product
        product_id = str(uuid.uuid4())
        self.client.get(
            f"http://localhost:8011/api/v1/{self.site_id or 'demo-site'}/products/{product_id}",
            name="/api/products/[id]",
            catch_response=True
        )

    @task
    def add_to_cart(self):
        """Add product to cart."""
        if not self.cart_id:
            # Create cart first
            response = self.client.post(
                f"http://localhost:8011/api/v1/{self.site_id or 'demo-site'}/cart",
                json={"session_id": self.session_id},
                name="/api/cart"
            )
            if response.status_code == 200:
                self.cart_id = response.json().get("cart_id")

        if self.cart_id:
            self.client.post(
                f"http://localhost:8011/api/v1/{self.site_id or 'demo-site'}/cart/{self.cart_id}/items",
                json={
                    "product_id": str(uuid.uuid4()),
                    "quantity": random.randint(1, 3)
                },
                name="/api/cart/items"
            )

    @task
    def view_cart(self):
        """View cart contents."""
        if self.cart_id:
            self.client.get(
                f"http://localhost:8011/api/v1/{self.site_id or 'demo-site'}/cart/{self.cart_id}",
                name="/api/cart/[id]"
            )


class BookingUserBehavior(SequentialTaskSet):
    """
    Simulates a customer booking an appointment.
    """

    def on_start(self):
        """Initialize booking session."""
        self.site_slug = "demo-salon"
        self.site_id = None

    @task
    def browse_services(self):
        """Browse available services."""
        self.client.get(
            f"http://localhost:8012/api/v1/{self.site_id or 'demo-site'}/services",
            name="/api/services"
        )

    @task
    def check_availability(self):
        """Check service availability."""
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        self.client.post(
            f"http://localhost:8012/api/v1/{self.site_id or 'demo-site'}/availability",
            json={
                "service_id": str(uuid.uuid4()),
                "booking_date": tomorrow
            },
            name="/api/availability"
        )

    @task
    def view_providers(self):
        """View available providers."""
        self.client.get(
            f"http://localhost:8012/api/v1/{self.site_id or 'demo-site'}/providers",
            name="/api/providers"
        )


class MixedUser(HttpUser):
    """
    Simulates mixed traffic - some users browse storefront, some book appointments.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    tasks = {
        StorefrontUserBehavior: 7,  # 70% storefront traffic
        BookingUserBehavior: 3,     # 30% booking traffic
    }


class StorefrontOnlyUser(HttpUser):
    """Heavy storefront traffic for targeted testing."""
    wait_time = between(0.5, 2)
    tasks = [StorefrontUserBehavior]


class BookingOnlyUser(HttpUser):
    """Heavy booking traffic for targeted testing."""
    wait_time = between(1, 3)
    tasks = [BookingUserBehavior]


class SpikeUser(HttpUser):
    """
    Simulates traffic spike - rapid requests with minimal wait time.
    """
    wait_time = between(0.1, 0.5)

    @task(10)
    def rapid_product_browse(self):
        """Rapidly browse products."""
        self.client.get(
            f"http://localhost:8011/api/v1/demo-site/products",
            params={"page": random.randint(1, 10)},
            name="/api/products"
        )

    @task(5)
    def rapid_service_browse(self):
        """Rapidly browse services."""
        self.client.get(
            f"http://localhost:8012/api/v1/demo-site/services",
            name="/api/services"
        )

    @task(1)
    def health_check(self):
        """Health check endpoints."""
        services = [8010, 8011, 8012, 8013, 8014, 8015]
        port = random.choice(services)
        self.client.get(
            f"http://localhost:{port}/health",
            name="/health"
        )
