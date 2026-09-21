"""
access_review_tracker.py

Automated Access Review Tracker
--------------------------------
Simulates a periodic user access review / access certification exercise,
the kind of IAM governance activity covered in SoD reviews, privileged
access reviews, and user access certifications.

WHAT THIS DOES:
1. Loads a user access export (CSV)
2. Applies a set of least-privilege / access-governance rules to flag
   accounts that should be reviewed or remediated
3. Produces:
   - A remediation report (CSV) listing every flagged account, the
     violation type, and a recommended action
   - A summary printed to the console (violation counts by category)

RULES APPLIED (each mirrors a real access-governance control):

  R1. Dormant account       -> no login in 90+ days, but still active
  R2. Terminated but active -> employment_status = Terminated, but the
                                account has not been revoked (this maps
                                to Straight-Through Revocation / STR)
  R3. Unapproved privileged  -> Privileged Admin or Super Admin access
       access                 with no recorded manager approval (SoD /
                                approval-chain violation)
  R4. Excessive standing      -> Super Admin access held by a non-IT
       privilege                department (segregation-of-duties flag)

You can extend RULES_APPLIED with more checks - that's part of the point:
a real access-review tool grows as new violation patterns are identified.
"""

import pandas as pd
from datetime import datetime

INPUT_FILE = "access_export_sample.csv"
OUTPUT_FILE = "access_review_remediation_report.csv"

DORMANT_THRESHOLD_DAYS = 90
PRIVILEGED_LEVELS = {"Privileged Admin", "Super Admin"}
IT_DEPARTMENTS = {"IT Operations", "Engineering"}


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def flag_dormant_accounts(df: pd.DataFrame) -> pd.DataFrame:
    """R1: Accounts with no login activity beyond the dormancy threshold."""
    flagged = df[
        (df["days_since_login"] > DORMANT_THRESHOLD_DAYS)
        & (df["employment_status"] == "Active")
    ].copy()
    flagged["violation_type"] = "Dormant Account"
    flagged["recommended_action"] = (
        "Confirm with manager whether access is still required; "
        "disable if unused for " + str(DORMANT_THRESHOLD_DAYS) + "+ days."
    )
    return flagged


def flag_terminated_but_active(df: pd.DataFrame) -> pd.DataFrame:
    """R2: Employment terminated, but access has not been revoked."""
    flagged = df[df["employment_status"] == "Terminated"].copy()
    flagged["violation_type"] = "Terminated User - Access Not Revoked"
    flagged["recommended_action"] = (
        "URGENT: Trigger Straight-Through Revocation (STR) immediately."
    )
    return flagged


def flag_unapproved_privileged_access(df: pd.DataFrame) -> pd.DataFrame:
    """R3: Privileged/Super Admin access without recorded manager approval."""
    flagged = df[
        (df["access_level"].isin(PRIVILEGED_LEVELS))
        & (df["manager_approved"] == "No")
    ].copy()
    flagged["violation_type"] = "Unapproved Privileged Access"
    flagged["recommended_action"] = (
        "Escalate to manager for retroactive approval or revoke access."
    )
    return flagged


def flag_sod_violations(df: pd.DataFrame) -> pd.DataFrame:
    """R4: Super Admin access held outside expected IT/Engineering scope."""
    flagged = df[
        (df["access_level"] == "Super Admin")
        & (~df["department"].isin(IT_DEPARTMENTS))
    ].copy()
    flagged["violation_type"] = "Segregation of Duties (SoD) Flag"
    flagged["recommended_action"] = (
        "Review business justification; Super Admin access outside "
        "IT/Engineering requires explicit SoD exception approval."
    )
    return flagged


def run_review(input_file: str = INPUT_FILE, output_file: str = OUTPUT_FILE):
    df = load_data(input_file)
    print(f"Loaded {len(df)} access records from {input_file}\n")

    results = [
        flag_dormant_accounts(df),
        flag_terminated_but_active(df),
        flag_unapproved_privileged_access(df),
        flag_sod_violations(df),
    ]

    report = pd.concat(results, ignore_index=True)
    report = report.sort_values(by=["violation_type", "user_id"])

    report.to_csv(output_file, index=False)

    print("=" * 60)
    print("ACCESS REVIEW SUMMARY")
    print("=" * 60)
    print(f"Total records reviewed:        {len(df)}")
    print(f"Total flagged violations:      {len(report)}")
    print(f"Unique accounts flagged:       {report['user_id'].nunique()}")
    print("-" * 60)
    print("Violations by category:")
    print(report["violation_type"].value_counts().to_string())
    print("-" * 60)
    print(f"Full remediation report written to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    run_review()
