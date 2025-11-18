from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from app.database import Base

class Widget(Base):
    __tablename__ = "widgets"
    widget_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    widget_type = Column(String(50), nullable=False)  # testimonial, cta, form, etc.
    template = Column(String(500))
    config = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WidgetInstance(Base):
    __tablename__ = "widget_instances"
    instance_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    widget_id = Column(UUID(as_uuid=True), ForeignKey("widgets.widget_id"))
    placement = Column(String(100))  # header, footer, sidebar, etc.
    settings = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
