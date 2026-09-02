# Collections Analytics Assignment

## What this project is about

This project looks at a collections business that reported an **11% month-on-month improvement in recovery**.

The main goal was not just to reproduce that number.

I wanted to check whether the improvement was actually meaningful, whether data-quality issues were affecting the result, what was driving the change, and what I would recommend doing with the next **₹10 Cr** of investment.

The analysis covers the full process from raw data to the final recommendation:

```text
Raw Data
   ↓
Data Quality Checks
   ↓
Golden Dataset
   ↓
Business Analysis
   ↓
Attribution / Statistical Checks
   ↓
Investment Recommendation
```

---

# Project Structure

```text
collections_assignment_ready/
│
├── data/
│   ├── raw/
│   └── golden/
│
├── notebook/
│   └── 01_golden_dataset.ipynb
│
├── sql/
│   ├── 01_staging.sql
│   ├── 02_cleaning.sql
│   └── 03_golden.sql
│
├── reports/
│   ├── data_quality_report.md
│   └── executive_memo.md
│
├── dashboard/
│   └── dashboard.html
│
├── architecture/
│   └── architecture.md
│
├── build_golden.py
├── README.md
└── SETUP_GUIDE.md
```

---

# What I worked on

## 1. Data quality and Golden Dataset

I started by profiling the raw files and checking whether the major identifiers were reliable.

The main problems I found were:

- repeated payment IDs
- duplicate call events
- borrower identity conflicts
- repeated agent records
- missing borrower and agent links
- multiple timezones
- incomplete attribution coverage

I used these checks to create a cleaner Golden Dataset rather than calculating the business metrics directly from the raw tables.

---

# 2. Golden Dataset

The main canonical datasets are:

| Entity | Golden Rows |
|---|---:|
| Borrowers | 11,015 |
| Accounts | 30,000 |
| Agents | 1,000 |
| Calls | 90,079 |
| Payments | 25,000 |

The Golden Dataset is used as the main analytical source of truth.

The raw files are still kept unchanged so that the transformation can be checked or rerun later.

---

# 3. Important data-quality finding

The payment table was the most important issue I found.

There were:

- 25,500 raw payment rows
- 25,000 unique payment IDs
- 500 repeated payment IDs
- 486 exact duplicate rows

After canonicalizing the payment data, successful recovery changed from approximately:

**₹134.15 Cr**

to:

**₹131.56 Cr**

A difference of approximately:

**₹2.59 Cr**

This showed me that data cleaning was not just a technical exercise. It could materially change the business result.

---

# 4. Main business finding

The reported February → March gross recovery increase is:

**+11.03%**

At first glance this looks positive.

However, the eligible portfolio also increased.

When I looked at recovery per eligible account instead:

**-18.37%**

So the more useful interpretation is:

> **Gross recovery increased, but recovery efficiency per eligible account declined.**

This is why I did not treat the 11% headline as enough evidence for a full investment decision.

---

# 5. Collection activity

March had higher collection activity and higher PTP creation than February.

At the same time, the portfolio's risk and loan-type mix was broadly stable.

This means activity appears related to the movement in recovery, but the data does not establish that a specific operational change caused the improvement.

I therefore classify this as **strong evidence/correlation**, not causal proof.

---

# 6. Payment attribution

A payment may happen after multiple interactions.

For example:

```text
CALL
  ↓
SMS
  ↓
WHATSAPP
  ↓
PAYMENT
```

Because of this, I tested different attribution windows including:

- 7 days
- 14 days
- 30 days

Using a 30-day latest-touch view, approximately **40% of successful recovery value had no recorded interaction within the attribution window**.

I therefore treat latest-touch attribution as a descriptive reporting method rather than proof that a specific channel caused the payment.

---

# 7. Statistical investigation

I also checked whether the movement could be explained by the underlying population rather than an actual operational improvement.

The investigation covered:

- portfolio mix
- account cohorts
- selection effects
- survivorship bias
- Simpson's paradox
- attribution-window effects
- time-series movement

The overall conclusion was that the data supports a change in observed recovery, but does not provide a clean causal explanation.

---

# 8. ₹10 Cr investment recommendation

The recommendation is:

## Better Borrower Targeting

I would use the ₹10 Cr to improve targeting, but I would **not deploy the full amount without a controlled test**.

The reason is straightforward:

The dataset contains useful targeting signals such as:

- DPD
- risk segment
- loan type
- outstanding amount
- previous collection activity
- historical recovery

These can be used to create a treatment group and a comparable control group.

The primary KPI should be:

**Incremental recovery per eligible account**

---

# 9. Financial scenarios

The current decision scenarios are:

| Scenario | Uplift | Incremental Recovery | Net Value | ROI |
|---|---:|---:|---:|---:|
| Downside | 2% | ₹4.35 Cr | -₹5.65 Cr | -56.51% |
| Base | 5% | ₹10.87 Cr | ₹0.87 Cr | 8.73% |
| Upside | 10% | ₹21.75 Cr | ₹11.75 Cr | 117.45% |

The approximate break-even uplift is:

**4.6%**

These numbers are scenario estimates, not guaranteed causal returns.

---

# Files in the project

## Notebook

`notebook/01_golden_dataset.ipynb`

Contains the main analysis, including:

- data profiling
- quality checks
- deduplication
- Golden Dataset logic
- recovery analysis
- attribution
- portfolio checks
- selection/survivorship checks
- counterfactual design
- investment scenarios

---

## SQL

### `sql/01_staging.sql`

Defines the staging layer and source table structure.

### `sql/02_cleaning.sql`

Contains cleaning, deduplication and canonicalization logic.

### `sql/03_golden.sql`

Defines the Golden analytical layer and reconciliation checks.

The SQL is written in a PostgreSQL-style format and may need small changes for a different warehouse.

---

## Data Quality Report

`reports/data_quality_report.md`

Documents:

- duplicate records
- identity conflicts
- missing values
- broken relationships
- payment reconciliation
- attribution limitations
- cleaning decisions
- business impact

---

## Executive Memo

`reports/executive_memo.md`

Contains the decision-oriented summary:

- what happened
- why the headline needs context
- confidence level
- investment recommendation
- expected financial impact
- downside and upside scenarios

---

## Dashboard

`dashboard/dashboard.html`

A standalone dashboard containing the main executive findings.

A Power BI version can be created from the Golden datasets using the same metric definitions.

---

## Architecture

`architecture/architecture.md`

Documents the production design:

```text
Raw
 ↓
Staging
 ↓
Clean
 ↓
Golden
 ↓
Feature
 ↓
Metrics
 ↓
Dashboard
```

It also covers data contracts, quality checks, attribution, incremental processing, late-arriving data, backfills, monitoring and experimentation.

---

# How to reproduce the analysis

The easiest way to review the work is:

### Step 1

Open the project folder in VS Code.

### Step 2

Open:

`notebook/01_golden_dataset.ipynb`

### Step 3

Run the notebook from top to bottom.

The notebook automatically looks for:

```text
data/raw/
```

inside the project.

### Step 4

Review the generated Golden datasets in:

```text
data/golden/
```

### Step 5

Review the supporting reports:

```text
reports/
```

### Step 6

Open:

```text
dashboard/dashboard.html
```

for the executive view.

---

# A few decisions I made deliberately

I tried to keep the analysis conservative.

For example:

- I did not invent borrower matches when a relationship could not be supported.
- I did not treat open PTPs as failed promises.
- I did not delete valid calls just because the agent ID was missing.
- I did not use raw payment totals after finding duplicate payment records.
- I did not treat latest-touch attribution as causal attribution.

These decisions were made to avoid making the data look cleaner than it actually is.

---

# Final takeaway

The biggest lesson from the project is that the **11% recovery headline is not necessarily the same thing as an 11% improvement in collection performance**.

The gross recovery number increased, but recovery per eligible account declined.

The data also contains enough duplication and attribution overlap that I would not use the current observational data to claim a causal uplift.

My recommended next step is therefore:

> **Test better borrower targeting with a controlled pilot, measure incremental recovery, and scale only if the economics are proven.**

---

## Main deliverables

```text
✅ Golden Dataset
✅ Data Quality Report
✅ Analysis Notebook
✅ SQL Repository
✅ Executive Memo
✅ Architecture
✅ Dashboard
✅ README
```