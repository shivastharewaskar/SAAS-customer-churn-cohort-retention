"""
Project 1: SaaS Customer Churn & Cohort Retention Analysis
Script: churn_exploratory_analysis.py
Performs end-to-end exploratory data analysis (EDA), cohort survival breakdown,
and statistical risk factor analysis using standard Python libraries.
"""

import csv
import os
from collections import defaultdict

def run_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "saas_subscriptions.csv")
    
    total_customers = 0
    churned_customers = 0
    total_mrr = 0.0
    churned_mrr = 0.0
    
    tier_stats = defaultdict(lambda: {"total": 0, "churned": 0, "mrr_lost": 0.0})
    ticket_stats = defaultdict(lambda: {"total": 0, "churned": 0, "mrr_lost": 0.0})
    channel_stats = defaultdict(lambda: {"total": 0, "churned": 0, "mrr_lost": 0.0})
    reasons_stats = defaultdict(int)
    
    with open(data_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_customers += 1
            mrr = float(row["monthly_recurring_revenue"])
            total_mrr += mrr
            tier = row["subscription_tier"]
            channel = row["acquisition_channel"]
            tickets = int(row["support_tickets_first_30d"])
            status = row["subscription_status"]
            reason = row["cancellation_reason"]
            
            is_churned = (status == "Churned")
            if is_churned:
                churned_customers += 1
                churned_mrr += mrr
                reasons_stats[reason] += 1
                
            tier_stats[tier]["total"] += 1
            channel_stats[channel]["total"] += 1
            ticket_stats[tickets]["total"] += 1
            
            if is_churned:
                tier_stats[tier]["churned"] += 1
                tier_stats[tier]["mrr_lost"] += mrr
                channel_stats[channel]["churned"] += 1
                channel_stats[channel]["mrr_lost"] += mrr
                ticket_stats[tickets]["churned"] += 1
                ticket_stats[tickets]["mrr_lost"] += mrr

    overall_churn_rate = (churned_customers / total_customers) * 100
    overall_mrr_loss_pct = (churned_mrr / total_mrr) * 100
    
    print("=" * 80)
    print("           SAAS SUBSCRIPTION & CHURN ANALYTICS - EXECUTIVE SUMMARY          ")
    print("=" * 80)
    print(f"Total Accounts Analyzed:       {total_customers:,}")
    print(f"Total Churned Accounts:        {churned_customers:,} ({overall_churn_rate:.2f}%)")
    print(f"Total MRR In-Scope:            ${total_mrr:,.2f}")
    print(f"Total MRR Lost to Churn:       ${churned_mrr:,.2f} ({overall_mrr_loss_pct:.2f}%)")
    print(f"Annualized Run-Rate Loss (ARR):${churned_mrr * 12:,.2f}")
    print("-" * 80)
    
    print("\n1. ONBOARDING FRICTION: SUPPORT TICKETS (FIRST 30 DAYS) VS. CHURN RATE")
    print(f"{'Tickets Count':<16} | {'Total Users':<12} | {'Churned Users':<14} | {'Churn Rate %':<14} | {'Lost MRR ($)':<12}")
    print("-" * 80)
    for t in sorted(ticket_stats.keys()):
        stat = ticket_stats[t]
        c_rate = (stat["churned"] / stat["total"]) * 100 if stat["total"] > 0 else 0
        print(f"{t:<16} | {stat['total']:<12} | {stat['churned']:<14} | {c_rate:<13.2f}% | ${stat['mrr_lost']:<11,.2f}")
        
    print("\n2. ACQUISITION CHANNEL EFFICIENCY & CHURN DECAY")
    print(f"{'Channel':<22} | {'Acquired':<10} | {'Churned':<10} | {'Churn Rate %':<14} | {'MRR Leakage ($)':<15}")
    print("-" * 80)
    for ch, stat in sorted(channel_stats.items(), key=lambda x: (x[1]["churned"] / x[1]["total"]), reverse=True):
        c_rate = (stat["churned"] / stat["total"]) * 100
        print(f"{ch:<22} | {stat['total']:<10} | {stat['churned']:<10} | {c_rate:<13.2f}% | ${stat['mrr_lost']:<14,.2f}")
        
    print("\n3. PRIMARY CANCELLATION DRIVERS")
    print(f"{'Reason':<45} | {'Count':<8} | {'% of Total Churn':<15}")
    print("-" * 80)
    for r, count in sorted(reasons_stats.items(), key=lambda x: x[1], reverse=True):
        pct = (count / churned_customers) * 100 if churned_customers > 0 else 0
        print(f"{r:<45} | {count:<8} | {pct:<14.2f}%")
    print("=" * 80)

if __name__ == "__main__":
    run_analysis()
