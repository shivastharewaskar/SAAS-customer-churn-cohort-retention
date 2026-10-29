-- ==============================================================================
-- PROJECT 1: SaaS Customer Churn & Cohort Retention Engine
-- SCRIPT: 01_schema_and_ingestion.sql
-- DESCRIPTION: Database DDL, indexing, and ingestion schema (PostgreSQL & SQLite compatible)
-- AUTHOR: Shivastha Rewaskar
-- ==============================================================================

DROP TABLE IF EXISTS subscriptions;

CREATE TABLE subscriptions (
    customer_id                  VARCHAR(20) PRIMARY KEY,
    signup_date                  DATE NOT NULL,
    cohort_month                 VARCHAR(7) NOT NULL, -- Format: YYYY-MM
    customer_industry            VARCHAR(50),
    acquisition_channel          VARCHAR(50) NOT NULL,
    subscription_tier            VARCHAR(20) NOT NULL, -- Starter, Growth, Enterprise
    monthly_recurring_revenue    DECIMAL(10, 2) NOT NULL,
    support_tickets_first_30d    INTEGER DEFAULT 0,
    product_adoption_score       INTEGER CHECK (product_adoption_score BETWEEN 0 AND 100),
    payment_failures_count       INTEGER DEFAULT 0,
    subscription_status          VARCHAR(20) NOT NULL, -- Active, Churned
    last_login_date              DATE NOT NULL,
    cancellation_date            DATE,
    cancellation_reason          VARCHAR(150)
);

-- Recommended Indexes for Analytics and High Performance Aggregations
CREATE INDEX idx_sub_cohort ON subscriptions (cohort_month);
CREATE INDEX idx_sub_status ON subscriptions (subscription_status);
CREATE INDEX idx_sub_tier ON subscriptions (subscription_tier);
CREATE INDEX idx_sub_signup ON subscriptions (signup_date);
CREATE INDEX idx_sub_cancel ON subscriptions (cancellation_date);
