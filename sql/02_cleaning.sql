
-- 02_cleaning.sql
-- Collections Analytics Assignment
--
-- Purpose:
-- Turn the staging data into cleaner, analysis-ready tables.
--
-- The main rules here came from the data-quality checks:
--   - keep one borrower profile per borrower_id
--   - keep one agent profile per agent_id
--   - remove exact duplicate call events
--   - keep one canonical payment per payment_id
--   - keep unresolved relationships visible instead of guessing
--
-- Dialect: PostgreSQL-style SQL

CREATE SCHEMA IF NOT EXISTS clean;


-- 1. BORROWERS

-- There are repeated borrower IDs in the raw file.
--
-- I use the most recently updated profile as the current
-- representative record, but I also keep a flag when the
-- borrower has more than one source record.
--
-- This is preferable to deleting borrowers with conflicts.

DROP TABLE IF EXISTS clean.borrowers;

CREATE TABLE clean.borrowers AS
SELECT
    borrower_id,
    name,
    phone,
    email,
    city,
    created_at,
    updated_at,
    state,

    CASE
        WHEN source_row_count > 1 THEN TRUE
        ELSE FALSE
    END AS identity_conflict_flag

FROM (
    SELECT
        b.*,

        COUNT(*) OVER (
            PARTITION BY borrower_id
        ) AS source_row_count,

        ROW_NUMBER() OVER (
            PARTITION BY borrower_id
            ORDER BY updated_at DESC NULLS LAST
        ) AS rn

    FROM staging.borrowers b
) x

WHERE rn = 1;


-- 2. ACCOUNTS

-- account_id is already unique in the source data.
--
-- The main issue here is borrower linkage, so I keep the
-- account and add explicit quality flags.

DROP TABLE IF EXISTS clean.accounts;

CREATE TABLE clean.accounts AS
SELECT
    a.*,

    CASE
        WHEN a.borrower_id IS NULL
        THEN TRUE
        ELSE FALSE
    END AS borrower_link_missing_flag,

    CASE
        WHEN a.borrower_id IS NOT NULL
         AND NOT EXISTS (
             SELECT 1
             FROM clean.borrowers b
             WHERE b.borrower_id = a.borrower_id
         )
        THEN TRUE
        ELSE FALSE
    END AS borrower_link_unresolved_flag

FROM staging.accounts a;


-- 3. AGENTS

-- agent_id is used as the canonical operational identifier.
--
-- When an agent appears more than once, keep the latest
-- available profile.

DROP TABLE IF EXISTS clean.agents;

CREATE TABLE clean.agents AS
SELECT
    agent_id,
    employee_code,
    agent_name,
    vendor_id,
    team,
    status,
    joined_at,
    updated_at

FROM (
    SELECT
        a.*,

        ROW_NUMBER() OVER (
            PARTITION BY agent_id
            ORDER BY updated_at DESC NULLS LAST
        ) AS rn

    FROM staging.agents a
) x

WHERE rn = 1;


-- 4. CALLS

-- Calls are event-level data.
--
-- Exact duplicate rows are removed.
--
-- I do not try to fill a missing agent_id because that would
-- create a relationship that is not supported by the source.

DROP TABLE IF EXISTS clean.calls;

CREATE TABLE clean.calls AS
SELECT DISTINCT
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

FROM staging.calls;


-- 5. PAYMENTS

-- payment_id is treated as the business event key.
--
-- A payment can appear multiple times in the raw data.
-- Instead of simply taking the first row, score each record
-- based on completeness and retain the most complete version.
--
-- The actual financial recovery calculation is done only on
-- the canonical payment table.

DROP TABLE IF EXISTS clean.payments;

CREATE TABLE clean.payments AS

WITH scored AS (
    SELECT
        p.*,

        (
            CASE WHEN account_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN borrower_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN event_at IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN amount IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN payment_status IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN payment_method IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN provider_id IS NOT NULL THEN 1 ELSE 0 END
        ) AS completeness_score

    FROM staging.payments p
),

ranked AS (
    SELECT
        scored.*,

        ROW_NUMBER() OVER (
            PARTITION BY payment_id
            ORDER BY
                completeness_score DESC,
                event_at DESC NULLS LAST
        ) AS rn

    FROM scored
)

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

FROM ranked

WHERE rn = 1;



-- 6. SIMPLE DATA-QUALITY SUMMARY

-- This table gives a quick view of what remains flagged after
-- cleaning. The detailed investigation is documented separately
-- in reports/data_quality_report.md.

DROP TABLE IF EXISTS clean.data_quality_summary;

CREATE TABLE clean.data_quality_summary AS

SELECT
    'borrowers' AS table_name,
    COUNT(*) AS rows_after_cleaning,
    SUM(
        CASE
            WHEN identity_conflict_flag
            THEN 1
            ELSE 0
        END
    ) AS flagged_rows

FROM clean.borrowers


UNION ALL


SELECT
    'accounts' AS table_name,
    COUNT(*) AS rows_after_cleaning,
    SUM(
        CASE
            WHEN borrower_link_missing_flag
              OR borrower_link_unresolved_flag
            THEN 1
            ELSE 0
        END
    ) AS flagged_rows

FROM clean.accounts


UNION ALL


SELECT
    'agents' AS table_name,
    COUNT(*) AS rows_after_cleaning,
    0 AS flagged_rows

FROM clean.agents


UNION ALL


SELECT
    'calls' AS table_name,
    COUNT(*) AS rows_after_cleaning,
    SUM(
        CASE
            WHEN agent_id IS NULL
            THEN 1
            ELSE 0
        END
    ) AS flagged_rows

FROM clean.calls


UNION ALL


SELECT
    'payments' AS table_name,
    COUNT(*) AS rows_after_cleaning,
    0 AS flagged_rows

FROM clean.payments;

