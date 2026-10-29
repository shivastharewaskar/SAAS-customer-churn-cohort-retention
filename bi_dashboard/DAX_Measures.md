# Power BI / DAX Formulas & Business Logic Reference
**Project:** SaaS Customer Churn & Cohort Retention Engine  
**Author:** Shivastha Rewaskar  

This document details the production-ready DAX measures implemented in Power BI to analyze customer cohort decay, retention curves, and revenue churn.

---

### 1. Base Metrics

#### Total Customers Acquired
```dax
Total Customers = DISTINCTCOUNT(subscriptions[customer_id])
```

#### Total Active Subscriptions
```dax
Active Subscriptions = 
CALCULATE(
    DISTINCTCOUNT(subscriptions[customer_id]),
    subscriptions[subscription_status] = "Active"
)
```

#### Total Churned Subscriptions
```dax
Churned Subscriptions = 
CALCULATE(
    DISTINCTCOUNT(subscriptions[customer_id]),
    subscriptions[subscription_status] = "Churned"
)
```

#### Overall Churn Rate %
```dax
Customer Churn Rate % = 
DIVIDE(
    [Churned Subscriptions],
    [Total Customers],
    0
)
```

---

### 2. Revenue & Financial DAX Measures

#### Current Monthly Recurring Revenue (MRR)
```dax
Active MRR = 
CALCULATE(
    SUM(subscriptions[monthly_recurring_revenue]),
    subscriptions[subscription_status] = "Active"
)
```

#### Churned MRR (Revenue Leakage)
```dax
Lost Churn MRR = 
CALCULATE(
    SUM(subscriptions[monthly_recurring_revenue]),
    subscriptions[subscription_status] = "Churned"
)
```

#### Average Revenue Per Account (ARPA)
```dax
ARPA = 
DIVIDE(
    [Active MRR],
    [Active Subscriptions],
    0
)
```

#### Estimated Customer Lifetime Value (LTV)
$$\text{LTV} = \frac{\text{ARPA}}{\text{Monthly Churn Rate}}$$
```dax
Estimated Customer LTV = 
VAR MonthlyChurn = DIVIDE([Churned Subscriptions], [Total Customers], 0)
RETURN
    IF(MonthlyChurn > 0, DIVIDE([ARPA], MonthlyChurn, 0), BLANK())
```

---

### 3. Cohort Retention Heatmap DAX Measures

#### Cohort Period Offset (Month Index: 0, 1, 2, ... 11)
```dax
Cohort Month Number = 
DATEDIFF(
    subscriptions[signup_date],
    COALESCE(subscriptions[cancellation_date], TODAY()),
    MONTH
)
```

#### Cohort Size (Month 0 Base)
```dax
Cohort Starting Base = 
CALCULATE(
    [Total Customers],
    ALLEXCEPT(subscriptions, subscriptions[cohort_month])
)
```

#### Cohort Retention Rate %
```dax
Cohort Retention Rate % = 
VAR InitialBase = [Cohort Starting Base]
VAR ActiveInCohort = [Total Customers] - [Churned Subscriptions]
RETURN
    DIVIDE(ActiveInCohort, InitialBase, 0)
```

---

### 4. Early Warning Churn Score (Conditional Flag)
```dax
Account Churn Risk Category = 
SWITCH(
    TRUE(),
    SELECTEDVALUE(subscriptions[support_tickets_first_30d]) >= 3, "Critical Risk (Red)",
    SELECTEDVALUE(subscriptions[support_tickets_first_30d]) = 2, "High Risk (Amber)",
    SELECTEDVALUE(subscriptions[product_adoption_score]) < 40, "Adoption Lag (Yellow)",
    "Healthy Account (Green)"
)
```
