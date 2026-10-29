# Power BI Dashboard Architecture & Wireframe Blueprint
**Project:** SaaS Customer Churn & Cohort Retention Engine  
**Author:** Shivastha Rewaskar  

---

### Dashboard Layout & Wireframe Grid (16:9 Canvas)

```
+-----------------------------------------------------------------------------------------------+
|  COMPANY LOGO  |  SAAS RETENTION & REVENUE COHORT INTELLIGENCE  |  SLICERS: Tier | Channel | Date |
+-----------------------------------------------------------------------------------------------+
| [ KPI 1: Active MRR ]  | [ KPI 2: Churn Rate % ] | [ KPI 3: MRR Churned ] | [ KPI 4: Est. LTV ]|
|      $575.1K           |        25.67%           |        $190.1K         |       $497.20      |
+-----------------------------------------------------------------------------------------------+
|  VISUAL A: Cohort Retention Matrix (Heatmap Grid)     |  VISUAL B: 30-Day Support Tickets vs. |
|  - Rows: Cohort Month (2025-01 to 2025-12)            |            Churn Rate (Clustered Bar) |
|  - Columns: Month Offset (M0, M1, M2 ... M11)         |  - 0 Tickets: 19% Churn               |
|  - Values: Retention Rate % (Green -> Red Gradient)   |  - 2 Tickets: 48.9% Churn             |
|                                                       |  - 3+ Tickets: 64% Churn              |
+-----------------------------------------------------------------------------------------------+
|  VISUAL C: Channel CAC vs. Churn Breakdown            |  VISUAL D: Early Warning Priority Triage
|  - Paid Social vs. Referral vs. Organic               |  - Table: High Risk Active Accounts   |
|  - Donut Chart: Cancellation Primary Drivers          |  - Columns: Client ID | MRR | Action  |
+-----------------------------------------------------------------------------------------------+
```

### Visual Specifications & Interaction Rules
1. **Interactive Cross-Filtering:**
   - Clicking any cohort cell filters Visual B and D to display specific accounts that churned within that window.
   - Slicers for `Subscription Tier` (Starter, Growth, Enterprise) allow VP of Sales to isolate enterprise churn.
2. **Color Palette Strategy:**
   - Primary: Deep Slate Navy (`#1E293B`)
   - Accent / Healthy: Emerald Green (`#10B981`)
   - Warning: Amber (`#F59E0B`)
   - Danger / Churned: Crimson Red (`#EF4444`)
