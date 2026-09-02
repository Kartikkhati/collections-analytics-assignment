-- 01_staging.sql
-- Collections Analytics Assignment
--
-- Purpose:
-- Create a typed staging layer for the main source tables.
--
-- This layer should stay close to the raw data.
-- Business logic and canonicalization happen in the cleaning/golden steps.

CREATE SCHEMA IF NOT EXISTS staging;


-- 1. Borrowers

DROP TABLE IF EXISTS staging.borrowers;

CREATE TABLE staging.borrowers (
    borrower_id      TEXT,
    name             TEXT,
    phone            TEXT,
    email            TEXT,
    city             TEXT,
    created_at       TIMESTAMP,
    updated_at       TIMESTAMP,
    state            TEXT
);


-- 2. Accounts


DROP TABLE IF EXISTS staging.accounts;

CREATE TABLE staging.accounts (
    account_id            TEXT,
    borrower_id           TEXT,
    loan_type              TEXT,
    principal_amount      NUMERIC,
    outstanding_amount    NUMERIC,
    dpd                    INTEGER,
    risk_segment           TEXT,
    status                 TEXT,
    opened_at              TIMESTAMP,
    timezone               TEXT,
    schema_version        TEXT
);


-- 3. Agents


DROP TABLE IF EXISTS staging.agents;

CREATE TABLE staging.agents (
    agent_id          TEXT,
    employee_code     TEXT,
    agent_name        TEXT,
    vendor_id         TEXT,
    team              TEXT,
    status            TEXT,
    joined_at         TIMESTAMP,
    updated_at        TIMESTAMP
);



-- 4. Calls


DROP TABLE IF EXISTS staging.calls;

CREATE TABLE staging.calls (
    call_id           TEXT,
    account_id        TEXT,
    borrower_id       TEXT,
    event_at          TIMESTAMP,
    agent_id          TEXT,
    campaign_id       TEXT,
    direction         TEXT,
    vendor_id         TEXT,
    call_status       TEXT,
    duration_sec      INTEGER,
    timezone          TEXT
);


-- 5. Payments


DROP TABLE IF EXISTS staging.payments;

CREATE TABLE staging.payments (
    payment_id        TEXT,
    account_id        TEXT,
    borrower_id       TEXT,
    event_at           TIMESTAMP,
    payment_reference TEXT,
    amount             NUMERIC,
    payment_status     TEXT,
    payment_method     TEXT,
    provider_id        TEXT
);

