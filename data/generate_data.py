"""
SaaS Customer Subscription & Churn Data Generator
Generates realistic, mathematically consistent subscription records across 12 months.
Simulates real business dynamics:
- Cohort decay (higher drop-off in month 1-2)
- High support tickets in first 30 days strongly correlates with churn
- Pricing tier sensitivity (Starter vs. Growth vs. Enterprise)
- Failed payment events and billing friction
"""

import csv
import random
import datetime
import os

random.seed(42)

TOTAL_CUSTOMERS = 6000
START_DATE = datetime.date(2025, 1, 1)
END_DATE = datetime.date(2025, 12, 31)

CHANNELS = ["Organic Search", "Paid Social", "Referral", "Cold Outbound", "Webinar / Events"]
TIERS = {
    "Starter": {"fee": 49.00, "base_churn_prob": 0.08},
    "Growth": {"fee": 149.00, "base_churn_prob": 0.05},
    "Enterprise": {"fee": 499.00, "base_churn_prob": 0.02}
}
INDUSTRIES = ["Fintech", "Healthtech", "E-commerce", "Edtech", "Logistics", "Marketing SaaS"]
CANCEL_REASONS = [
    "Unresolved Technical Issues / Support Latency",
    "Pricing / Budget Constraints",
    "Missing Core Integrations",
    "Switched to Competitor",
    "Low Internal Adoption / Champion Left Company",
    "Payment Gateway / Invoicing Friction"
]

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + datetime.timedelta(days=random_days)

def generate_records():
    records = []
    
    for customer_id in range(1001, 1001 + TOTAL_CUSTOMERS):
        signup = random_date(START_DATE, END_DATE)
        channel = random.choices(CHANNELS, weights=[0.35, 0.25, 0.20, 0.12, 0.08])[0]
        tier = random.choices(["Starter", "Growth", "Enterprise"], weights=[0.55, 0.35, 0.10])[0]
        fee = TIERS[tier]["fee"]
        industry = random.choice(INDUSTRIES)
        
        # Support tickets in first 30 days
        tickets_prob = random.random()
        if tickets_prob < 0.50:
            tickets_30d = 0
        elif tickets_prob < 0.80:
            tickets_30d = 1
        elif tickets_prob < 0.93:
            tickets_30d = 2
        else:
            tickets_30d = random.randint(3, 5)
            
        # Feature adoption score (1 to 100)
        # Higher tickets or poor channel might lead to lower adoption
        adoption_score = random.randint(30, 95)
        if tickets_30d >= 2:
            adoption_score = max(10, adoption_score - random.randint(15, 30))
        if channel == "Paid Social":
            adoption_score = max(10, adoption_score - 10)
            
        # Calculate Churn Probability
        churn_risk = TIERS[tier]["base_churn_prob"]
        
        # Unresolved tickets heavily increase churn risk
        if tickets_30d >= 3:
            churn_risk += 0.40
        elif tickets_30d == 2:
            churn_risk += 0.22
            
        # Low adoption increases churn risk
        if adoption_score < 40:
            churn_risk += 0.35
        elif adoption_score < 60:
            churn_risk += 0.15
            
        # Channel dynamics
        if channel == "Paid Social":
            churn_risk += 0.12
        elif channel == "Referral":
            churn_risk -= 0.08
            
        churn_risk = max(0.01, min(0.92, churn_risk))
        
        is_churned = random.random() < churn_risk
        
        cancellation_date = None
        cancellation_reason = "Active"
        payment_failures = 0
        
        if is_churned:
            # When did they churn? Typically within 1-6 months after signup
            max_tenure_days = max(15, (END_DATE - signup).days)
            tenure_days = random.randint(15, max_tenure_days)
            cancellation_date = signup + datetime.timedelta(days=tenure_days)
            if cancellation_date > END_DATE:
                # Still active as of cutoff
                is_churned = False
                cancellation_date = None
            else:
                if tickets_30d >= 2:
                    cancellation_reason = "Unresolved Technical Issues / Support Latency"
                elif adoption_score < 40:
                    cancellation_reason = random.choice(["Low Internal Adoption / Champion Left Company", "Switched to Competitor"])
                else:
                    cancellation_reason = random.choice(CANCEL_REASONS)
                
                payment_failures = random.choices([0, 1, 2, 3], weights=[0.6, 0.25, 0.10, 0.05])[0]
                
        status = "Churned" if is_churned else "Active"
        
        # User login activity
        if status == "Active":
            days_since_last_login = random.randint(0, 14)
            last_login = END_DATE - datetime.timedelta(days=days_since_last_login)
        else:
            # churned users stopped logging in shortly before cancellation
            days_before_cancel = random.randint(1, 10)
            last_login = cancellation_date - datetime.timedelta(days=days_before_cancel)
            
        records.append({
            "customer_id": f"CUST-{customer_id}",
            "signup_date": signup.strftime("%Y-%m-%d"),
            "cohort_month": signup.strftime("%Y-%m"),
            "customer_industry": industry,
            "acquisition_channel": channel,
            "subscription_tier": tier,
            "monthly_recurring_revenue": fee,
            "support_tickets_first_30d": tickets_30d,
            "product_adoption_score": adoption_score,
            "payment_failures_count": payment_failures,
            "subscription_status": status,
            "last_login_date": last_login.strftime("%Y-%m-%d"),
            "cancellation_date": cancellation_date.strftime("%Y-%m-%d") if cancellation_date else "",
            "cancellation_reason": cancellation_reason
        })
        
    return records

def save_csv():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(output_dir, "saas_subscriptions.csv")
    
    records = generate_records()
    fieldnames = list(records[0].keys())
    
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Generated {len(records)} realistic records at {file_path}")

if __name__ == "__main__":
    save_csv()
