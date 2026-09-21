"""
generate_sample_data.py

Creates a synthetic user-access export, similar in shape to what you'd pull
from an IAM/GRC platform (ServiceNow, Archer, SailPoint, Azure AD, etc.)
for a periodic access review.

This is fake data — no real people, no real company. It exists purely to
give the access_review_tracker.py script something realistic to analyze.
"""

import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible output

departments = ["Finance", "Engineering", "HR", "Sales", "Risk & Compliance", "IT Operations"]
applications = ["Payments-Core", "CRM-Salesforce", "HR-Workday", "GL-SAP", "Trade-Finance-App", "Data-Warehouse"]
access_levels = ["Read-Only", "Standard User", "Privileged Admin", "Super Admin"]

def random_date(start_days_ago, end_days_ago):
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")

rows = []
for i in range(1, 151):
    user_id = f"U{1000 + i}"
    dept = random.choice(departments)
    app = random.choice(applications)
    access_level = random.choices(access_levels, weights=[40, 35, 18, 7])[0]

    # Most accounts log in regularly; a smaller minority have gone dormant.
    # This mirrors a realistic environment better than a flat distribution.
    if random.random() < 0.78:
        last_login = random_date(60, 0)       # regularly used
    else:
        last_login = random_date(400, 91)     # dormant candidate
    days_since_login = (datetime.today() - datetime.strptime(last_login, "%Y-%m-%d")).days

    account_created = random_date(1200, 400)
    manager_approved = random.choices(["Yes", "No"], weights=[88, 12])[0]
    employment_status = random.choices(["Active", "Terminated"], weights=[94, 6])[0]

    rows.append({
        "user_id": user_id,
        "department": dept,
        "application": app,
        "access_level": access_level,
        "account_created": account_created,
        "last_login": last_login,
        "days_since_login": days_since_login,
        "manager_approved": manager_approved,
        "employment_status": employment_status,
    })

df = pd.DataFrame(rows)
df.to_csv("access_export_sample.csv", index=False)
print(f"Generated {len(df)} sample access records -> access_export_sample.csv")
