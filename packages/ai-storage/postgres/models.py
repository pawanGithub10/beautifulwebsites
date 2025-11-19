"""
Database models for token usage tracking
"""

from sqlalchemy import Column, String, Integer, DateTime, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class AITokenUsage(Base):
    """
    Token usage tracking table.

    Tracks all AI API calls for billing and analytics.
    """
    __tablename__ = "ai_token_usage"

    usage_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Feature and model
    feature = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)

    # Token counts
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)

    # Cost
    estimated_cost = Column(Numeric(10, 6), nullable=False)

    # Reference (optional - links to product, review, etc.)
    reference_type = Column(String(50))
    reference_id = Column(UUID(as_uuid=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_month = Column(
        String(7),
        nullable=False,
        index=True
    )  # YYYY-MM for monthly queries

    # Indexes for common queries
    __table_args__ = (
        Index('idx_token_usage_site_month', 'site_id', 'created_month'),
        Index('idx_token_usage_feature', 'feature'),
        Index('idx_token_usage_created', 'created_at'),
    )

    def __repr__(self):
        return (
            f"<AITokenUsage(site={self.site_id}, feature={self.feature}, "
            f"tokens={self.total_tokens}, cost=${self.estimated_cost})>"
        )


class SiteQuota(Base):
    """
    Site quota limits table.

    Defines token quotas per site for billing tiers.
    """
    __tablename__ = "site_quotas"

    quota_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)

    # Quota limits
    monthly_token_limit = Column(Integer, nullable=False)

    # Billing tier
    tier = Column(String(20), nullable=False)  # free, starter, professional, enterprise

    # Status
    is_active = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<SiteQuota(site={self.site_id}, tier={self.tier}, "
            f"limit={self.monthly_token_limit})>"
        )
