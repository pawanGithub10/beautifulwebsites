"""Database models for Lead Service"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class LeadForm(Base):
    """Configurable lead capture forms"""
    __tablename__ = "lead_forms"
    
    form_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Form configuration (JSONB with field definitions)
    fields = Column(JSONB, default=list)  # [{name, type, required, validation}]
    settings = Column(JSONB, default=dict)  # {redirect_url, success_message, etc.}
    
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leads = relationship("Lead", back_populates="form")
    
    __table_args__ = (
        Index('ix_lead_forms_site_slug', 'site_id', 'slug'),
    )


class Lead(Base):
    """Captured leads"""
    __tablename__ = "leads"
    
    lead_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    form_id = Column(UUID(as_uuid=True), ForeignKey("lead_forms.form_id"), nullable=True)
    
    # Contact information
    name = Column(String(200), nullable=False)
    email = Column(String(200), index=True)
    phone = Column(String(20), index=True)
    company = Column(String(200))
    
    # Lead data (flexible JSONB for custom form fields)
    data = Column(JSONB, default=dict)
    
    # Lead management
    status = Column(String(20), default='new', index=True)  # new, contacted, qualified, converted, lost
    score = Column(Integer, default=0, index=True)  # Lead score (0-100)
    source = Column(String(100))  # organic, paid, referral, etc.
    assigned_to_user_id = Column(UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacted_at = Column(DateTime)
    qualified_at = Column(DateTime)
    converted_at = Column(DateTime)
    lost_at = Column(DateTime)
    
    # Relationships
    form = relationship("LeadForm", back_populates="leads")
    notes = relationship("LeadNote", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_leads_site_status', 'site_id', 'status'),
        Index('ix_leads_site_score', 'site_id', 'score'),
    )


class LeadNote(Base):
    """Notes on leads"""
    __tablename__ = "lead_notes"
    
    note_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.lead_id"), nullable=False)
    
    content = Column(Text, nullable=False)
    created_by_user_id = Column(UUID(as_uuid=True))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="notes")
    
    __table_args__ = (
        Index('ix_lead_notes_lead', 'lead_id'),
    )


class LeadActivity(Base):
    """Activity tracking for leads"""
    __tablename__ = "lead_activities"
    
    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.lead_id"), nullable=False)
    
    activity_type = Column(String(50), nullable=False)  # call, email, meeting, note, status_change
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Activity metadata
    metadata = Column(JSONB, default=dict)  # {duration, outcome, next_steps, etc.}
    
    created_by_user_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="activities")
    
    __table_args__ = (
        Index('ix_lead_activities_lead_type', 'lead_id', 'activity_type'),
    )
