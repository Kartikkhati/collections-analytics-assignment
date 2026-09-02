-- 03_golden.sql
-- Collections Analytics Assignment

-- Purpose:
-- Publish the cleaned tables as the Golden analytical layer.
--
-- Golden = the version of the data used for downstream analysis.
--
-- Dialect: PostgreSQL-style SQL


CREATE SCHEMA IF NOT EXISTS golden;


-- 1. GOLDEN BORROWERS

-- One canonical row per borrower_id.

DROP TABLE IF EXISTS golden.borrowers;

CREATE TABLE golden.borrowers AS
SELECT
    borrower_id,
    name,
    phone,
    email,
    city,
    created_at,
    updated_at,
    state,
    identity_conflict_flag
FROM clean.borrowers;


-- 2. GOLDEN ACCOUNTS

-- Keep all accounts because account_id is already unique.
-- Borrower-link problems remain visible through the flags.

DROP TABLE IF EXISTS golden.accounts;

CREATE TABLE golden.accounts AS
SELECT
    account_id,
    borrower_id,
    loan_type,
    principal_amount,
    outstanding_amount,
    dpd,
    risk_segment,
    status,
    opened_at,
    timezone,
    schema_version,
    borrower_link_missing_flag,
    borrower_link_unresolved_flag
FROM clean.accounts;


-- 3. GOLDEN AGENTS

-- One canonical profile per agent_id.

DROP TABLE IF EXISTS golden.agents;

CREATE TABLE golden.agents AS
SELECT
    agent_id,
    employee_code,
    agent_name,
    vendor_id,
    team,
    status,
    joined_at,
    updated_at
FROM clean.agents;


-- 4. GOLDEN CALLS

-- Calls are already deduplicated in the clean layer.
-- Missing agent IDs are intentionally retained.

DROP TABLE IF EXISTS golden.calls;

CREATE TABLE golden.calls AS
SELECT
    call_id,
    account_id,
    borrower_id,
    event_at,
    agent_id,
    campaign_id,
    direction,
    vendor_id,
    call_status,
    duration_sec,
    timezone
FROM clean.calls;


-- 5. GOLDEN PAYMENTS

-- One canonical event per payment_id.

DROP TABLE IF EXISTS golden.payments;

CREATE TABLE golden.payments AS
SELECT
    payment_id,
    account_id,
    borrower_id,
    event_at,
    payment_reference,
    amount,
    payment_status,
    payment_method,
    provider_id
FROM clean.payments;


-- 6. GOLDEN DATA CHECKS

-- These checks help confirm that the published Golden layer
-- behaves as expected.

-- Borrowers should have one row per borrower_id.
-- SELECT borrower_id, COUNT(*)
-- FROM golden.borrowers
-- GROUP BY borrower_id
-- HAVING COUNT(*) > 1;


-- Accounts should have one row per account_id.
-- SELECT account_id, COUNT(*)
-- FROM golden.accounts
-- GROUP BY account_id
-- HAVING COUNT(*) > 1;


-- Agents should have one row per agent_id.
-- SELECT agent_id, COUNT(*)
-- FROM golden.agents
-- GROUP BY agent_id
-- HAVING COUNT(*) > 1;


-- Calls should have one row per call_id.
-- SELECT call_id, COUNT(*)
-- FROM golden.calls
-- GROUP BY call_id
-- HAVING COUNT(*) > 1;


-- Payments should have one row per payment_id.
-- SELECT payment_id, COUNT(*)
-- FROM golden.payments
-- GROUP BY payment_id
-- HAVING COUNT(*) > 1;


-- 7. GOLDEN ROW-COUNT SUMMARY


DROP TABLE IF EXISTS golden.row_count_summary;

CREATE TABLE golden.row_count_summary AS

SELECT
    'borrowers' AS entity,
    COUNT(*) AS golden_rows
FROM golden.borrowers

UNION ALL

SELECT
    'accounts',
    COUNT(*)
FROM golden.accounts

UNION ALL

SELECT
    'agents',
    COUNT(*)
FROM golden.agents

UNION ALL

SELECT
    'calls',
    COUNT(*)
FROM golden.calls

UNION ALL

SELECT
    'payments',
    COUNT(*)
FROM golden.payments;


-- 8. PAYMENT RECOVERY RECONCILIATION

-- Compare the successful payment amount before and after
-- canonicalization.
--
-- This is the main financial quality check in the project.

DROP TABLE IF EXISTS golden.payment_reconciliation;

CREATE TABLE golden.payment_reconciliation AS

SELECT
    'Raw staging' AS dataset,
    COUNT(*) AS payment_rows,
    SUM(
        CASE
            WHEN payment_status = 'SUCCESS'
             AND amount > 0
            THEN amount
            ELSE 0
        END
    ) AS successful_recovery
FROM staging.payments

UNION ALL

SELECT
    'Golden',
    COUNT(*),
    SUM(
        CASE
            WHEN payment_status = 'SUCCESS'
             AND amount > 0
            THEN amount
            ELSE 0
        END
    )
FROM golden.payments;


-- 9. GOLDEN ACCOUNT QUALITY SUMMARY

-- Keep the unresolved borrower relationship visible so that
-- downstream users know which account records have linkage issues.

DROP TABLE IF EXISTS golden.account_quality_summary;

CREATE TABLE golden.account_quality_summary AS

SELECT
    COUNT(*) AS total_accounts,

    SUM(
        CASE
            WHEN borrower_link_missing_flag
            THEN 1
            ELSE 0
        END
    ) AS missing_borrower_id,

    SUM(
        CASE
            WHEN borrower_link_unresolved_flag
            THEN 1
            ELSE 0
        END
    ) AS unresolved_borrower_id

FROM golden.accounts;
