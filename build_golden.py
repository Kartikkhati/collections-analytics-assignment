from pathlib import Path
import pandas as pd
import numpy as np



# Collections Analytics Assignment
# Golden Dataset Builder

# The raw CSV files are never modified.
# This script creates the canonical Golden datasets and
# a few audit files that explain what changed during cleaning.


# 1. Project paths


possible_roots = [
    Path(__file__).resolve().parent,
    Path(__file__).resolve().parent.parent
]

PROJECT_ROOT = next(
    (
        p for p in possible_roots
        if (p / "data" / "raw").exists()
    ),
    None
)

if PROJECT_ROOT is None:
    raise FileNotFoundError(
        "Could not find the project root containing data/raw."
    )

RAW = PROJECT_ROOT / "data" / "raw"
GOLDEN = PROJECT_ROOT / "data" / "golden"

GOLDEN.mkdir(parents=True, exist_ok=True)

print("Project:", PROJECT_ROOT)
print("Raw data:", RAW)
print("Golden output:", GOLDEN)


# 2. Load the main tables


b = pd.read_csv(
    RAW / "borrowers.csv",
    parse_dates=["created_at", "updated_at"]
)

ag = pd.read_csv(
    RAW / "agents.csv",
    parse_dates=["joined_at", "updated_at"]
)

ac = pd.read_csv(
    RAW / "accounts.csv",
    parse_dates=["opened_at"]
)

ca = pd.read_csv(
    RAW / "calls.csv",
    parse_dates=["event_at"]
)

p = pd.read_csv(
    RAW / "payments.csv",
    parse_dates=["event_at"]
)


# 3. Audit helper


audits = []


def add_audit(
    dataset,
    raw_rows,
    golden_rows,
    exact_dups_removed=0,
    conflicts=0,
    null_key_rows=0,
    notes=""
):
    audits.append({
        "dataset": dataset,
        "raw_rows": raw_rows,
        "golden_rows": golden_rows,
        "rows_removed": raw_rows - golden_rows,
        "exact_duplicate_rows_removed": exact_dups_removed,
        "conflicting_identifier_rows_flagged": conflicts,
        "null_key_rows": null_key_rows,
        "notes": notes
    })


# 4. Borrowers

#
# Rule:
# - remove exact duplicate source rows
# - check profile conflicts per borrower_id
# - keep the latest updated profile
# - retain a conflict flag


b["source_row_number"] = np.arange(1, len(b) + 1)

borrower_compare_cols = [
    c for c in b.columns
    if c != "source_row_number"
]

b["exact_duplicate_flag"] = b.duplicated(
    subset=borrower_compare_cols,
    keep="first"
)

raw_b = b.copy()

b_clean = b.loc[
    ~b["exact_duplicate_flag"]
].copy()

profile_cols = [
    "name",
    "phone",
    "email",
    "city",
    "state"
]

conf = (
    b_clean
    .groupby("borrower_id")
    .agg(
        **{
            f"{c}_nunique": (c, "nunique")
            for c in profile_cols
        }
    )
    .reset_index()
)

conflict_cols = [
    f"{c}_nunique"
    for c in profile_cols
]

conf["borrower_profile_conflict_flag"] = (
    conf[conflict_cols]
    .gt(1)
    .any(axis=1)
    .astype(int)
)

b_clean = b_clean.merge(
    conf[
        [
            "borrower_id",
            "borrower_profile_conflict_flag"
        ]
    ],
    on="borrower_id",
    how="left"
)

b_clean = b_clean.sort_values(
    [
        "borrower_id",
        "updated_at",
        "source_row_number"
    ]
)

golden_borrowers = (
    b_clean
    .groupby("borrower_id", as_index=False)
    .tail(1)
    .copy()
)

golden_borrowers["profile_snapshot_rule"] = (
    "latest_updated_at_after_exact_dedup"
)

golden_borrowers = golden_borrowers.drop(
    columns=[
        "source_row_number",
        "exact_duplicate_flag"
    ]
)

add_audit(
    "borrowers",
    len(raw_b),
    len(golden_borrowers),
    exact_dups_removed=int(
        raw_b["exact_duplicate_flag"].sum()
    ),
    conflicts=int(
        conf["borrower_profile_conflict_flag"].sum()
    ),
    null_key_rows=int(
        raw_b["borrower_id"].isna().sum()
    ),
    notes=(
        "One representative profile retained per borrower_id. "
        "Profile conflicts are flagged instead of silently reconciled."
    )
)


# 5. Accounts

#
# account_id is already unique in the source.
# Missing borrower IDs are kept and flagged.


ac["source_row_number"] = np.arange(1, len(ac) + 1)

ac["borrower_link_missing_flag"] = (
    ac["borrower_id"].isna()
).astype(int)

golden_accounts = ac.drop(
    columns=["source_row_number"]
).copy()

add_audit(
    "accounts",
    len(ac),
    len(golden_accounts),
    null_key_rows=int(
        ac["account_id"].isna().sum()
    ),
    notes=(
        "account_id retained as the account grain. "
        "Missing borrower IDs are flagged, not imputed."
    )
)


# 6. Agents


ag["source_row_number"] = np.arange(1, len(ag) + 1)

agent_profile_cols = [
    "employee_code",
    "agent_name",
    "vendor_id",
    "team",
    "status",
    "joined_at"
]

ag_conf = (
    ag
    .groupby("agent_id")
    .agg(
        **{
            f"{c}_nunique": (c, "nunique")
            for c in agent_profile_cols
        }
    )
    .reset_index()
)

agent_conflict_cols = [
    f"{c}_nunique"
    for c in agent_profile_cols
]

ag_conf["agent_profile_conflict_flag"] = (
    ag_conf[agent_conflict_cols]
    .gt(1)
    .any(axis=1)
    .astype(int)
)

tag = ag.merge(
    ag_conf[
        [
            "agent_id",
            "agent_profile_conflict_flag"
        ]
    ],
    on="agent_id",
    how="left"
)

tag["employee_code_not_unique_global_flag"] = (
    tag["employee_code"]
    .duplicated(keep=False)
    .astype(int)
)

tag = tag.sort_values(
    [
        "agent_id",
        "updated_at",
        "source_row_number"
    ]
)

golden_agents = (
    tag
    .groupby("agent_id", as_index=False)
    .tail(1)
    .copy()
)

golden_agents["profile_snapshot_rule"] = (
    "latest_updated_at_after_retaining_agent_id"
)

golden_agents = golden_agents.drop(
    columns=["source_row_number"]
)

add_audit(
    "agents",
    len(ag),
    len(golden_agents),
    conflicts=int(
        ag_conf["agent_profile_conflict_flag"].sum()
    ),
    null_key_rows=int(
        ag["agent_id"].isna().sum()
    ),
    notes=(
        "Latest profile retained per agent_id. "
        "employee_code is not used as a unique key."
    )
)


# 7. Calls

#
# Exact duplicate events are removed.
# Reused/conflicting call IDs remain visible.
# Account master is preferred for borrower resolution.


ca["source_row_number"] = np.arange(1, len(ca) + 1)

call_compare_cols = [
    c for c in ca.columns
    if c != "source_row_number"
]

ca["exact_duplicate_flag"] = ca.duplicated(
    subset=call_compare_cols,
    keep="first"
)

raw_ca = ca.copy()

ca2 = ca.loc[
    ~ca["exact_duplicate_flag"]
].copy()

call_id_stats = (
    ca2
    .groupby("call_id")
    .agg(
        call_id_rows=("call_id", "size"),
        call_accounts=("account_id", "nunique"),
        call_times=("event_at", "nunique"),
        call_agents=("agent_id", "nunique"),
        call_statuses=("call_status", "nunique")
    )
    .reset_index()
)

call_id_stats["call_id_conflict_flag"] = (
    call_id_stats["call_id_rows"] > 1
).astype(int)

ca2 = ca2.merge(
    call_id_stats,
    on="call_id",
    how="left"
)

ca2 = ca2.merge(
    golden_accounts[
        [
            "account_id",
            "borrower_id"
        ]
    ],
    on="account_id",
    how="left",
    suffixes=("_raw", "_account")
)

ca2["borrower_resolution_rule"] = np.where(
    ca2["borrower_id_account"].notna(),
    "account_master",
    "raw_event_borrower"
)

ca2["borrower_id"] = (
    ca2["borrower_id_account"]
    .combine_first(
        ca2["borrower_id_raw"]
    )
)

ca2["borrower_id_mismatch_flag"] = (
    ca2["borrower_id_raw"].notna()
    & ca2["borrower_id_account"].notna()
    & (
        ca2["borrower_id_raw"]
        != ca2["borrower_id_account"]
    )
).astype(int)

ca2["account_missing_flag"] = (
    ca2["borrower_id_account"].isna()
).astype(int)

ca2["raw_borrower_id"] = (
    ca2["borrower_id_raw"]
)

ca2 = ca2.drop(
    columns=[
        "borrower_id_raw",
        "borrower_id_account"
    ]
)

ca2["event_timezone_present_flag"] = (
    ca2["timezone"].notna()
).astype(int)


def convert_to_utc(row):
    if pd.isna(row["event_at"]) or pd.isna(row["timezone"]):
        return pd.NaT

    try:
        return (
            row["event_at"]
            .tz_localize(
                row["timezone"],
                ambiguous="NaT",
                nonexistent="NaT"
            )
            .tz_convert("UTC")
            .tz_localize(None)
        )
    except Exception:
        return pd.NaT


ca2["event_at_utc"] = ca2.apply(
    convert_to_utc,
    axis=1
)

golden_calls = ca2.copy()

add_audit(
    "calls",
    len(raw_ca),
    len(golden_calls),
    exact_dups_removed=int(
        raw_ca["exact_duplicate_flag"].sum()
    ),
    conflicts=int(
        call_id_stats["call_id_conflict_flag"].sum()
    ),
    null_key_rows=int(
        raw_ca["call_id"].isna().sum()
    ),
    notes=(
        "Exact duplicate events removed. Reused/conflicting call IDs "
        "remain visible. Missing agent IDs are retained."
    )
)



# 8. Payments


# payment_id is the business event key.
#
# - remove exact duplicate rows
# - inspect repeated payment IDs
# - don't use payment_reference as a deduplication key
# - resolve borrower from account master where possible
# - retain one row per payment_id


p["source_row_number"] = np.arange(1, len(p) + 1)

payment_compare_cols = [
    c for c in p.columns
    if c != "source_row_number"
]

p["exact_duplicate_flag"] = p.duplicated(
    subset=payment_compare_cols,
    keep="first"
)

raw_p = p.copy()

p2 = p.loc[
    ~p["exact_duplicate_flag"]
].copy()

pid = (
    p2
    .groupby("payment_id")
    .agg(
        payment_id_rows=("payment_id", "size"),
        payment_accounts=("account_id", "nunique"),
        payment_times=("event_at", "nunique"),
        payment_statuses=("payment_status", "nunique")
    )
    .reset_index()
)

pid["payment_id_conflict_flag"] = (
    pid["payment_id_rows"] > 1
).astype(int)

p2 = p2.merge(
    pid,
    on="payment_id",
    how="left"
)

p2 = p2.merge(
    golden_accounts[
        [
            "account_id",
            "borrower_id"
        ]
    ],
    on="account_id",
    how="left",
    suffixes=("_raw", "_account")
)

p2["borrower_resolution_rule"] = np.where(
    p2["borrower_id_account"].notna(),
    "account_master",
    "raw_event_borrower"
)

p2["borrower_id"] = (
    p2["borrower_id_account"]
    .combine_first(
        p2["borrower_id_raw"]
    )
)

p2["borrower_id_mismatch_flag"] = (
    p2["borrower_id_raw"].notna()
    & p2["borrower_id_account"].notna()
    & (
        p2["borrower_id_raw"]
        != p2["borrower_id_account"]
    )
).astype(int)

p2["account_missing_flag"] = (
    p2["borrower_id_account"].isna()
).astype(int)

p2["raw_borrower_id"] = (
    p2["borrower_id_raw"]
)

p2 = p2.drop(
    columns=[
        "borrower_id_raw",
        "borrower_id_account"
    ]
)

reference_stats = (
    p2
    .groupby("payment_reference")
    .agg(
        reference_row_count=("payment_reference", "size"),
        reference_account_count=("account_id", "nunique")
    )
    .reset_index()
)

p2 = p2.merge(
    reference_stats,
    on="payment_reference",
    how="left"
)

p2["payment_reference_collision_flag"] = (
    (p2["reference_row_count"] > 1)
    & (p2["reference_account_count"] > 1)
).astype(int)

p2["is_valid_recovery"] = (
    p2["payment_status"].eq("SUCCESS")
    & p2["amount"].gt(0)
).astype(int)

# No per-row timezone exists in the payment source,
# so preserve the original event timestamp.
p2["event_at_utc"] = p2["event_at"]


# Choose the most complete record when payment_id is repeated.
completeness_cols = [
    "account_id",
    "borrower_id",
    "event_at",
    "payment_reference",
    "amount",
    "payment_status",
    "payment_method",
    "provider_id"
]

p2["completeness_score"] = (
    p2[completeness_cols]
    .notna()
    .sum(axis=1)
)

p2 = p2.sort_values(
    [
        "payment_id",
        "completeness_score",
        "event_at"
    ],
    ascending=[True, False, False]
)

golden_payments = (
    p2
    .drop_duplicates(
        "payment_id",
        keep="first"
    )
    .copy()
)

golden_payments = golden_payments.drop(
    columns=["completeness_score"]
)

add_audit(
    "payments",
    len(raw_p),
    len(golden_payments),
    exact_dups_removed=int(
        raw_p["exact_duplicate_flag"].sum()
    ),
    conflicts=int(
        pid["payment_id_conflict_flag"].sum()
    ),
    null_key_rows=int(
        raw_p["payment_id"].isna().sum()
    ),
    notes=(
        "Exact duplicates removed first. Repeated payment IDs are "
        "resolved using record completeness. payment_reference is "
        "not used as the deduplication key."
    )
)


# 9. Cleaning impact


audit_df = pd.DataFrame(audits)

audit_df["reduction_pct"] = (
    100
    * audit_df["rows_removed"]
    / audit_df["raw_rows"]
)


raw_success = raw_p.loc[
    raw_p["payment_status"].eq("SUCCESS")
    & raw_p["amount"].gt(0),
    "amount"
].sum()

golden_success = golden_payments.loc[
    golden_payments["is_valid_recovery"].eq(1),
    "amount"
].sum()


impact = pd.DataFrame([
    {
        "metric": "raw_borrower_rows",
        "raw_value": len(raw_b),
        "golden_value": len(golden_borrowers),
        "delta": len(golden_borrowers) - len(raw_b)
    },
    {
        "metric": "raw_account_rows",
        "raw_value": len(ac),
        "golden_value": len(golden_accounts),
        "delta": len(golden_accounts) - len(ac)
    },
    {
        "metric": "raw_agent_rows",
        "raw_value": len(ag),
        "golden_value": len(golden_agents),
        "delta": len(golden_agents) - len(ag)
    },
    {
        "metric": "raw_call_rows",
        "raw_value": len(raw_ca),
        "golden_value": len(golden_calls),
        "delta": len(golden_calls) - len(raw_ca)
    },
    {
        "metric": "raw_payment_rows",
        "raw_value": len(raw_p),
        "golden_value": len(golden_payments),
        "delta": len(golden_payments) - len(raw_p)
    },
    {
        "metric": "successful_payment_amount",
        "raw_value": raw_success,
        "golden_value": golden_success,
        "delta": golden_success - raw_success
    }
])


# 10. Exclusion log


exclusions = []


for _, row in raw_b.loc[
    raw_b["exact_duplicate_flag"]
].iterrows():
    exclusions.append({
        "dataset": "borrowers",
        "record_id": row["borrower_id"],
        "reason_code": "EXACT_DUPLICATE",
        "action": "REJECT",
        "detail": "Exact duplicate borrower snapshot removed."
    })


for _, row in raw_ca.loc[
    raw_ca["exact_duplicate_flag"]
].iterrows():
    exclusions.append({
        "dataset": "calls",
        "record_id": row["call_id"],
        "reason_code": "EXACT_DUPLICATE",
        "action": "REJECT",
        "detail": "Exact duplicate call event removed."
    })


for _, row in raw_p.loc[
    raw_p["exact_duplicate_flag"]
].iterrows():
    exclusions.append({
        "dataset": "payments",
        "record_id": row["payment_id"],
        "reason_code": "EXACT_DUPLICATE",
        "action": "REJECT",
        "detail": "Exact duplicate payment event removed."
    })

excl_df = pd.DataFrame(exclusions)


# 11. Write outputs

outputs = {
    "golden_borrowers.csv": golden_borrowers,
    "golden_accounts.csv": golden_accounts,
    "golden_agents.csv": golden_agents,
    "golden_calls.csv": golden_calls,
    "golden_payments.csv": golden_payments,
    "data_quality_audit.csv": audit_df,
    "cleaning_impact.csv": impact,
    "data_quality_exclusions.csv": excl_df
}

for filename, df in outputs.items():
    df.to_csv(
        GOLDEN / filename,
        index=False
    )


# 12. Final summary


print("\n" + "=" * 60)
print("GOLDEN DATASET BUILD COMPLETE")
print("=" * 60)

print("\nGolden row counts:")
print(
    audit_df[
        [
            "dataset",
            "raw_rows",
            "golden_rows",
            "rows_removed"
        ]
    ].to_string(index=False)
)

print("\nSuccessful recovery reconciliation:")
print(
    "Raw successful recovery:    ₹{:,.2f}".format(
        raw_success
    )
)
print(
    "Golden successful recovery: ₹{:,.2f}".format(
        golden_success
    )
)
print(
    "Difference:                 ₹{:,.2f}".format(
        golden_success - raw_success
    )
)

print("\nGolden output:")
print(GOLDEN)