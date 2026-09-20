Access Review Tracker

A Python tool that simulates a periodic user-access review / access certification exercise — the kind of IAM governance activity behind segregation-of-duties (SoD) reviews, privileged access reviews, and user access certifications

What it does
generate_sample_data.py creates a synthetic access export (150 records, 6 departments, 6 applications) — no real data, just a realistic shape to work with.
access_review_tracker.py loads that export and applies four access-governance rules:
Rule	Checks for	Maps to
R1	No login in 90+ days, account still active	Dormant account review
R2	Employment terminated, access not yet revoked	Straight-Through Revocation (STR)
R3	Privileged/Super Admin access with no recorded manager approval	Approval-chain / SoD violation
R4	Super Admin access held outside IT/Engineering	Segregation of duties (SoD)

Outputs access_review_remediation_report.csv — every flagged account, its violation type, and a recommended remediation action — plus a console summary.

Run it yourself
bash
pip install pandas
python generate_sample_data.py
python access_review_tracker.py

Why I built this
This mirrors the access-governance work I do day to day — SoD reviews, privileged access reviews, user access certification, and access revocation tracking — as a working example rather than just a resume bullet point. The rules engine is intentionally simple to extend: a real access review adds new violation patterns over time as an organization's risk posture evolves, and this is built the same way.
