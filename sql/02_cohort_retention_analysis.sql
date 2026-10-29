-- ==============================================================================
-- PROJECT 1: SaaS Customer Churn & Cohort Retention Engine
-- SCRIPT: 02_cohort_retention_analysis.sql
-- DESCRIPTION: Monthly cohort retention matrix using CTEs and Window Functions
-- PURPOSE: Determines customer drop-off over 0 to 11 months post-acquisition
-- ==============================================================================

WITH base_cohort AS (
    -- Step 1: Establish cohort base size and signup month
    SELECT 
        customer_id,
        cohort_month,
        signup_date,
        subscription_status,
        cancellation_date,
        monthly_recurring_revenue
    FROM subscriptions
),

cohort_sizes AS (
    -- Step 2: Calculate total acquisitions per cohort (Month 0 base)
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_initial_users,
        SUM(monthly_recurring_revenue) AS cohort_initial_mrr
    FROM base_cohort
    GROUP BY cohort_month
),

active_months AS (
    -- Step 3: Map user retention across 12 calendar observation periods
    SELECT 
        b.cohort_month,
        b.customer_id,
        b.monthly_recurring_revenue,
        -- Generate month indices (Month 0, Month 1, Month 2, ...)
        m.month_offset
    FROM base_cohort b
    CROSS JOIN (
        SELECT 0 AS month_offset UNION ALL
        SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
        SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL
        SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL
        SELECT 10 UNION ALL SELECT 11
    ) m
    WHERE 
        -- User is considered active in month_offset if they haven't cancelled before that point
        (b.cancellation_date IS NULL OR 
         (strftime('%Y', b.cancellation_date) * 12 + strftime('%m', b.cancellation_date)) - 
         (strftime('%Y', b.signup_date) * 12 + strftime('%m', b.signup_date)) > m.month_offset)
),

cohort_retention_summary AS (
    -- Step 4: Aggregate surviving users by cohort month and month offset
    SELECT 
        a.cohort_month,
        cs.cohort_initial_users,
        a.month_offset,
        COUNT(DISTINCT a.customer_id) AS active_users,
        SUM(a.monthly_recurring_revenue) AS active_mrr,
        ROUND((COUNT(DISTINCT a.customer_id) * 100.0) / cs.cohort_initial_users, 2) AS retention_rate_pct
    FROM active_months a
    JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
    GROUP BY a.cohort_month, cs.cohort_initial_users, a.month_offset
)

-- Step 5: Final output ready for dashboard cohort heatmaps
SELECT 
    cohort_month,
    cohort_initial_users,
    month_offset,
    active_users,
    retention_rate_pct,
    ROUND(100.0 - retention_rate_pct, 2) AS cumulative_churn_pct,
    active_mrr
FROM cohort_retention_summary
ORDER BY cohort_month, month_offset;
