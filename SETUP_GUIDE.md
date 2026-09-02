# Setup Guide

## Collections Analytics Assignment

This guide explains how to open and run the project locally.

The project was built using Python, Jupyter Notebook, pandas and SQL files. The dashboard is currently available as a standalone HTML file, while the main analysis is contained in the notebook.

---

## 1. What you need

You will need:

- Python 3
- VS Code
- Jupyter Notebook / Jupyter extension in VS Code
- pandas
- numpy

A virtual environment is recommended, but it is not strictly required for reviewing the project.

---

## 2. Open the project

Open the project folder in VS Code:

```text
collections_assignment_ready/
```

The important folders are:

```text
data/
notebook/
sql/
reports/
dashboard/
architecture/
```

---

## 3. Install Python packages

Open the VS Code terminal and run:

```bash
python3 -m pip install pandas numpy jupyter
```

If `python3` is not available, try:

```bash
python -m pip install pandas numpy jupyter
```

---

## 4. Open the notebook

Open:

```text
notebook/01_golden_dataset.ipynb
```

Select the Python 3 kernel when VS Code asks for one.

The notebook is designed to detect the project root automatically, so it should work without changing the local Mac/Windows path.

---

## 5. Run the analysis

Run the notebook from top to bottom.

In VS Code you can use:

**Run All**

or execute the cells one by one.

The notebook performs:

1. Raw data inventory
2. Primary-key checks
3. Borrower identity checks
4. Agent identity checks
5. Payment deduplication checks
6. Call quality checks
7. Missingness checks
8. Referential integrity checks
9. Timestamp/timezone checks
10. Recovery analysis
11. Portfolio mix analysis
12. Selection/survivorship checks
13. Payment attribution
14. PTP analysis
15. Agent productivity analysis
16. Vendor/campaign checks
17. Statistical investigation
18. Counterfactual design
19. Investment scenarios
20. Final recommendation

---

## 6. Golden Dataset

The cleaned analytical datasets are stored in:

```text
data/golden/
```

The main outputs are:

```text
golden_borrowers.csv
golden_accounts.csv
golden_agents.csv
golden_calls.csv
golden_payments.csv
```

These files are the main analytical source used after the cleaning process.

---

## 7. SQL files

The SQL folder contains three stages:

### `sql/01_staging.sql`

Creates the typed staging layer.

### `sql/02_cleaning.sql`

Contains cleaning and canonicalization logic such as:

- Duplicate handling
- Entity resolution
- Missing-data flags
- Referential checks

### `sql/03_golden.sql`

Defines the final Golden layer and reconciliation checks.

The SQL is written in a PostgreSQL-style format. It may require minor syntax changes depending on the warehouse being used.

The SQL is included as a production design/reference layer; the notebook is the easiest way to reproduce the analysis locally.

---

## 8. Data Quality Report

For a detailed explanation of the data problems and cleaning decisions, open:

```text
reports/data_quality_report.md
```

This explains:

- What was found
- How it was detected
- What was done about it
- How it affected the business analysis

---

## 9. Executive Memo

The main business recommendation is in:

```text
reports/executive_memo.md
```

This is the quickest document to read if you want the final answer without going through the full notebook.

It covers:

- What happened
- Why the 11% headline needs context
- Confidence level
- Investment recommendation
- Financial scenarios
- Proposed next step

---

## 10. Dashboard

The current standalone dashboard is:

```text
dashboard/dashboard.html
```

Open it in a browser.

It provides a quick view of:

- Recovery performance
- February → March movement
- PTP performance
- Payment attribution
- Data-quality issues
- Investment scenarios
- Final recommendation

A Power BI version can be built later using the same Golden data and metric definitions.

---

## 11. Architecture

The proposed production design is documented in:

```text
architecture/architecture.md
```

The architecture follows:

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

It also describes:

- Data contracts
- Primary keys
- Data-quality checks
- Lineage
- Incremental processing
- Late-arriving data
- Backfills
- Attribution
- Experimentation

---

## 12. Re-running after changing the raw data

If the raw CSV files are changed or replaced:

1. Keep the folder structure unchanged.
2. Re-run the notebook from the beginning.
3. Check the generated Golden datasets.
4. Re-check the data-quality findings.
5. Re-check the executive metrics.

Do not manually edit the Golden CSVs to force a desired result.

---

## 13. Recommended review order

Someone reviewing the project can use this order:

```text
README.md
   ↓
reports/executive_memo.md
   ↓
reports/data_quality_report.md
   ↓
notebook/01_golden_dataset.ipynb
   ↓
data/golden/
   ↓
sql/
   ↓
architecture/architecture.md
   ↓
dashboard/dashboard.html
```

For a quick review, start with the Executive Memo.

For the full analysis, start with the notebook.

---

## 14. Important interpretation note

The project deliberately separates:

**Observed movement**

from

**Causal impact**

For example:

> Gross recovery increased 11.03% from February to March.

This is an observed result.

It should not automatically be interpreted as:

> The targeting strategy caused an 11.03% improvement.

The current data is observational, so a controlled experiment or suitable quasi-experimental design is required to estimate causal impact.

---

## 15. Final project structure

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

## 16. Final note

The project is intended to be reproducible from the raw source data while keeping the analytical decisions visible.

The main principle is:

> **Do not start with the answer. Start by checking whether the data deserves to be trusted.**