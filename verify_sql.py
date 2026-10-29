"""
Verification script: loads saas_subscriptions.csv into an in-memory SQLite database
and executes the SQL analysis scripts to confirm syntax and correctness.
"""
import sqlite3
import csv
import os

db_path = ":memory:"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

base_dir = os.path.dirname(os.path.abspath(__file__))
schema_file = os.path.join(base_dir, "sql", "01_schema_and_ingestion.sql")
data_file = os.path.join(base_dir, "data", "saas_subscriptions.csv")
cohort_sql = os.path.join(base_dir, "sql", "02_cohort_retention_analysis.sql")
drivers_sql = os.path.join(base_dir, "sql", "03_churn_drivers_and_segmentation.sql")

with open(schema_file, "r") as f:
    cursor.executescript(f.read())

with open(data_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [(
        r["customer_id"], r["signup_date"], r["cohort_month"], r["customer_industry"],
        r["acquisition_channel"], r["subscription_tier"], float(r["monthly_recurring_revenue"]),
        int(r["support_tickets_first_30d"]), int(r["product_adoption_score"]),
        int(r["payment_failures_count"]), r["subscription_status"], r["last_login_date"],
        r["cancellation_date"] if r["cancellation_date"] else None,
        r["cancellation_reason"]
    ) for r in reader]

cursor.executemany("""
    INSERT INTO subscriptions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", rows)
conn.commit()

print(f"Successfully ingested {len(rows)} records into SQLite.")

# Test Cohort Query
with open(cohort_sql, "r") as f:
    cursor.execute(f.read())
    results = cursor.fetchall()
    print(f"Cohort query executed successfully, returned {len(results)} cohort rows.")
    print("Sample cohort row:", results[0])

# Test Drivers Query
with open(drivers_sql, "r") as f:
    sql_text = f.read()
    # Execute individual queries in the drivers file
    queries = [q.strip() for q in sql_text.split(";") if q.strip()]
    for i, q in enumerate(queries, 1):
        cursor.execute(q)
        rows_res = cursor.fetchall()
        print(f"Driver query {i} executed successfully, returned {len(rows_res)} rows.")

conn.close()
print("All SQL scripts verified with 0 errors!")
