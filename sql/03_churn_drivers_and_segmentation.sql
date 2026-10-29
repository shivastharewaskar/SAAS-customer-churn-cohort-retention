-- ==============================================================================
-- PROJECT 1: SaaS Customer Churn & Cohort Retention Engine
-- SCRIPT: 03_churn_drivers_and_segmentation.sql
-- DESCRIPTION: Multi-dimensional root cause analysis of churn triggers and MRR loss
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Support Ticket Friction Analysis (The 30-Day Onboarding Trap)
-- Demonstrates the exponential impact of early unresolved customer friction
-- ------------------------------------------------------------------------------
SELECT 
    support_tickets_first_30d,
    COUNT(customer_id) AS total_customers,
    SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN subscription_status = 'Churned' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(product_adoption_score), 1) AS avg_adoption_score,
    ROUND(SUM(CASE WHEN subscription_status = 'Churned' THEN monthly_recurring_revenue ELSE 0 END), 2) AS lost_mrr
FROM subscriptions
GROUP BY support_tickets_first_30d
ORDER BY support_tickets_first_30d;

-- ------------------------------------------------------------------------------
-- QUERY 2: Channel Quality vs. Churn Rate vs. Unit Economics
-- Determines which acquisition channels bring "High LTV" vs. "High Churn" users
-- ------------------------------------------------------------------------------
SELECT 
    acquisition_channel,
    COUNT(customer_id) AS total_acquired,
    ROUND(SUM(monthly_recurring_revenue), 2) AS total_mrr_acquired,
    SUM(CASE WHEN subscription_status = 'Churned' THEN 1 ELSE 0 END) AS churned_count,
    ROUND(SUM(CASE WHEN subscription_status = 'Churned' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(customer_id), 2) AS channel_churn_rate_pct,
    ROUND(AVG(product_adoption_score), 1) AS avg_adoption_score,
    ROUND(SUM(CASE WHEN subscription_status = 'Churned' THEN monthly_recurring_revenue ELSE 0 END), 2) AS total_mrr_leakage
FROM subscriptions
GROUP BY acquisition_channel
ORDER BY channel_churn_rate_pct DESC;

-- ------------------------------------------------------------------------------
-- QUERY 3: Tier Profitability & Cancellation Reason Taxonomy
-- Evaluates primary exit rationales across Starter, Growth, and Enterprise
-- ------------------------------------------------------------------------------
SELECT 
    subscription_tier,
    cancellation_reason,
    COUNT(customer_id) AS churn_instances,
    ROUND(SUM(monthly_recurring_revenue), 2) AS lost_mrr_contribution,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(PARTITION BY subscription_tier), 2) AS pct_of_tier_churn
FROM subscriptions
WHERE subscription_status = 'Churned'
GROUP BY subscription_tier, cancellation_reason
ORDER BY subscription_tier, lost_mrr_contribution DESC;

-- ------------------------------------------------------------------------------
-- QUERY 4: Proactive Churn Risk Scoring (For Customer Success Early Warning)
-- Flags active accounts at imminent risk of churn (Window Function + Scoring)
-- ------------------------------------------------------------------------------
WITH customer_risk_scored AS (
    SELECT 
        customer_id,
        subscription_tier,
        acquisition_channel,
        monthly_recurring_revenue,
        support_tickets_first_30d,
        product_adoption_score,
        payment_failures_count,
        -- Risk Index Calculation: 0 (Safe) to 100 (Critical Danger)
        (
            (CASE WHEN support_tickets_first_30d >= 3 THEN 40 
                  WHEN support_tickets_first_30d = 2 THEN 25 
                  ELSE 0 END) +
            (CASE WHEN product_adoption_score < 40 THEN 35 
                  WHEN product_adoption_score < 60 THEN 20 
                  ELSE 0 END) +
            (CASE WHEN payment_failures_count >= 2 THEN 25 
                  WHEN payment_failures_count = 1 THEN 10 
                  ELSE 0 END)
        ) AS churn_risk_score
    FROM subscriptions
    WHERE subscription_status = 'Active'
)
SELECT 
    customer_id,
    subscription_tier,
    monthly_recurring_revenue,
    churn_risk_score,
    CASE 
        WHEN churn_risk_score >= 60 THEN 'High Risk - Urgent Intervene'
        WHEN churn_risk_score >= 35 THEN 'Medium Risk - Monitor'
        ELSE 'Healthy Account'
    END AS risk_tier,
    DENSE_RANK() OVER (ORDER BY churn_risk_score DESC, monthly_recurring_revenue DESC) AS intervention_priority
FROM customer_risk_scored
ORDER BY churn_risk_score DESC, monthly_recurring_revenue DESC;
