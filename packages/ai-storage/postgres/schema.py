"""
Database initialization script
"""

SQL_SCHEMA = """
-- Token usage tracking table
CREATE TABLE IF NOT EXISTS ai_token_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,

    -- Feature and model
    feature VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,

    -- Token counts
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,

    -- Cost
    estimated_cost NUMERIC(10, 6) NOT NULL,

    -- Reference (optional)
    reference_type VARCHAR(50),
    reference_id UUID,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_month VARCHAR(7) NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_token_usage_site_month
    ON ai_token_usage(site_id, created_month);
CREATE INDEX IF NOT EXISTS idx_token_usage_feature
    ON ai_token_usage(feature);
CREATE INDEX IF NOT EXISTS idx_token_usage_created
    ON ai_token_usage(created_at);


-- Site quotas table
CREATE TABLE IF NOT EXISTS site_quotas (
    quota_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL UNIQUE,

    -- Quota limits
    monthly_token_limit INTEGER NOT NULL,

    -- Billing tier
    tier VARCHAR(20) NOT NULL,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_site_quotas_site
    ON site_quotas(site_id);


-- Function to auto-set created_month
CREATE OR REPLACE FUNCTION set_created_month()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_month := TO_CHAR(NEW.created_at, 'YYYY-MM');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-set created_month
DROP TRIGGER IF EXISTS trigger_set_created_month ON ai_token_usage;
CREATE TRIGGER trigger_set_created_month
    BEFORE INSERT ON ai_token_usage
    FOR EACH ROW
    EXECUTE FUNCTION set_created_month();
"""


async def init_database(db_url: str):
    """
    Initialize database schema.

    Args:
        db_url: Database connection URL
    """
    # Real implementation would use asyncpg
    # import asyncpg
    # conn = await asyncpg.connect(db_url)
    # await conn.execute(SQL_SCHEMA)
    # await conn.close()

    print("Database schema initialized")
    print(SQL_SCHEMA)


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_database("postgresql://localhost/ai_platform"))
