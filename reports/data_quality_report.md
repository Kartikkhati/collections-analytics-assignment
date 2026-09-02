# Data Quality Report

## Collections Analytics Assignment

### Why I did this check

Before looking at recovery performance, I wanted to understand how reliable the raw data actually was.

There are quite a few files in this project, and they do not all behave like simple one-row-per-customer tables. Some contain repeated events, some contain multiple versions of the same entity, and some have missing links to other tables.

So I did the data-quality checks first and built the Golden Dataset before using the data for the main analysis.

The main questions I wanted to answer were:

- Are there duplicates?
- Can I trust the main IDs?
- Are the same borrowers or agents appearing differently?
- How much information is missing?
- Can I safely join the main tables?
- Does cleaning the data materially change recovery?

The answer to the last question is YES.

---

# 1. What I Found First

There are 18 raw CSV files in the project covering accounts, borrowers, calls, payments, agents, PTPs, digital interactions and other collection activity.

The first thing that stood out was that the raw row count was not always the same as the number of real entities.

For example:

| Dataset | Raw Rows | Unique IDs |
|---|---:|---:|
| Borrowers | 30,600 | 11,015 |
| Accounts | 30,000 | 30,000 |
| Agents | 30,000 | 1,000 |
| Calls | 91,350 | 90,000 |
| Payments | 25,500 | 25,000 |

This was important because using raw row counts directly could easily inflate activity or recovery.

---

# 2. The Biggest Issue: Payments

The payment table was the issue I considered most important.

There are:

- 25,500 raw payment rows
- 25,000 unique payment IDs
- 500 repeated payment IDs
- 486 exact duplicate rows
- 14 repeated IDs where the details were not identical

I did not want to simply drop every repeated record because that could remove valid information.

Instead, I kept one canonical record for each `payment_id`, using the most complete valid record where duplicates existed.

## What changed after cleaning?

Raw successful recovery:

**₹134.15 Cr**

Golden successful recovery:

**₹131.56 Cr**

Difference:

**₹2.59 Cr**

That is a large enough difference to matter in an executive report.

This was probably the most useful finding from the data-quality work because it showed that **the cleaning process itself can change the business answer**.

For the final analysis, I therefore use the Golden payment data rather than the raw payment table.

---

# 3. Borrower Data Was Messier Than Expected

The borrower file has:

- 30,600 rows
- 11,015 unique borrower IDs
- 600 exact duplicate rows
- 8,518 borrower IDs with conflicting attributes

The conflicts mean that the same `borrower_id` can appear with different profile information.

I did not remove all of these borrowers.

Instead, I kept one canonical profile per borrower and retained an identity-conflict flag.

### Why?

Because removing all conflicting borrowers would make the dataset look cleaner, but it would also throw away potentially useful records.

My preference was to keep the borrower and make the problem visible.


# 4. Agent Data Also Has Repeated Records

The agent table contains:

- 30,000 rows
- 1,000 unique `agent_id` values
- 1,099 unique employee codes

Again, the raw row count is not an agent count.

I created one canonical agent record per `agent_id` and preferred the latest updated profile.

This matters mainly for agent productivity analysis, because duplicated agent records could otherwise make the same person appear more than once.


# 5. Calls: Duplicate Activity Can Inflate the Funnel

The calls table contains:

- 91,350 raw rows
- 90,000 unique call IDs
- 1,350 repeated call IDs
- 1,271 exact duplicate events

There were also 1,827 calls with no `agent_id`.

For the duplicate calls, I removed exact duplicate events.

For calls with a missing agent, I kept the call.

### Why keep them?

Because the call itself still happened and can still be useful for account-level collection analysis.

I did not want a missing agent field to make an otherwise valid call disappear.

Those records are treated as a quality exception instead.

The resulting Golden call dataset contains:

**90,079 rows**


# 6. Missing Data

There are missing values in a number of fields.

The main ones I found were:

| Field                        | Missing | Rate  |
| `accounts.borrower_id`       | 455     | 1.52% |
| `borrowers.email`            | 895     | 2.92% |
| `borrowers.phone`            | 614     | 2.01% |
| `call_attempts.vendor_id`    | 2,400   | 2.00% |
| `calls.agent_id`             | 1,827   | 2.00% |
| `field_visits.scheduled_at`  | 250     | 1.00% |
| `payments.payment_reference` | 382     | 1.50% |

I did not fill these values with guesses.

For the fields that matter for joins or attribution, I kept the missing values visible and flagged them.

This is especially important for `agent_id` and `borrower_id`, because filling those incorrectly could create fake relationships.

---

# 7. Account-to-Borrower Matching

This was another important join check.

I found:

- 2,458 account borrower IDs that do not match the borrower table
- 455 accounts with no borrower ID

So there are **2,913 accounts with an unresolved borrower relationship**.

I did not try to manually invent matches.

That means:

- account-level analysis is still possible
- some borrower-level analysis is less reliable
- borrower segmentation should be interpreted carefully

This is one of the limitations I would mention if presenting the analysis.

---

# 8. Other Relationship Checks

Some of the important joins were actually clean.

### Payment → Account

No invalid account IDs were identified.

### Call → Account

No invalid account IDs were identified.

### Call → Agent

1,827 calls have missing agent IDs.

This means payment/account joins are relatively strong, while some agent-level attribution is incomplete.

---

# 9. Time and Timezone Checks

The operational data comes from multiple timezones:

- Asia/Kolkata
- Asia/Dubai
- UTC

Call timestamps range from:

**29 Dec 2025 to 12 Aug 2026**

There were no missing call timestamps in the timestamp check.

The main thing I wanted to avoid here was accidentally putting an event into the wrong reporting day because of timezone differences.

For the analysis, the production design is to:

1. Keep the original timestamp.
2. Keep the original timezone.
3. Convert to UTC when comparing events across regions.
4. Use local time for operational reporting.

---

# 10. Account Status History

The account status table contains 60,000 records and represents account events over time rather than a single current status.

There are:

- 25,999 accounts represented in the history
- 17,821 accounts with multiple status events
- 16,521 accounts with multiple distinct statuses

The statuses include:

- ACTIVE
- DELINQUENT
- NPA
- PTP
- PAID
- CLOSED
- WRITEOFF

So I treated this table as a history/event table rather than trying to reduce it to one row per account.

There were also differences between `event_at` and `recorded_at`. The differences were generally around a day in either direction.

I kept both timestamps rather than overwriting one with the other.

---

# 11. PTP Data

There are 18,000 PTP records.

The status split is:

| Status    | Count |
| BROKEN    | 4,553 |
| CANCELLED | 4,543 |
| KEPT      | 4,489 |
| OPEN      | 4,415 |

At the time of analysis:

- 16,758 PTPs were mature
- 1,242 were still open / not yet mature

The final matured kept rate is:

**49.65%**

I used:

```text
KEPT
-------------------------
KEPT + BROKEN
```

for the kept-rate calculation.

I did **not** treat every open PTP as failed because some of them had not reached the promised date yet.

That distinction matters.

---

# 12. Payment Attribution Is Not a Clean One-to-One Problem

One payment can happen after several collection interactions.

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

So assigning the full payment to whichever channel happened last can be misleading.

For successful payments:

- 17,534 successful payments
- 13,284 successful-payment accounts
- 11,926 had a previous call
- 5,608 had no previous call

I therefore looked at 7-day, 14-day and 30-day attribution windows.

For the 30-day latest-touch view:

| Latest Touch | Payments | Recovery |
|---|---:|---:|
| No Prior Interaction | 7,052 | ₹52.63 Cr |
| Call | 4,280 | ₹32.22 Cr |
| WhatsApp | 2,815 | ₹21.18 Cr |
| SMS | 2,181 | ₹16.35 Cr |
| Field Visit | 1,206 | ₹9.17 Cr |

Around **40% of successful recovery value** falls into the no-prior-interaction category under this definition.

Because of this, I use latest-touch attribution as a descriptive view.

I would not claim that the last channel caused the payment.

---

# 13. The Recovery Denominator Needed Attention

One of the easiest ways to make the recovery number look better or worse is to use the wrong denominator.

The eligible portfolio changes over time, so using the same 30,000-account denominator for every month would not be appropriate.

For the monthly analysis I therefore used:

- Eligible accounts
- Eligible outstanding amount

This made the February-to-March comparison more useful.

The result is interesting:

**Gross recovery increased by 11.03%.**

But:

**Recovery per eligible account decreased by 18.37%.**

So the recovery increase is real, but it is not telling the whole story.

The portfolio itself was changing at the same time.

---

# 14. What Went Into the Golden Dataset

After the quality checks, I created canonical versions of the main analytical tables.

| Entity | Raw Rows | Golden Rows |
|---|---:|---:|
| Borrowers | 30,600 | 11,015 |
| Accounts | 30,000 | 30,000 |
| Agents | 30,000 | 1,000 |
| Calls | 91,350 | 90,079 |
| Payments | 25,500 | 25,000 |

The purpose of the Golden Dataset was not to hide bad records.

It was to:

- remove duplicates where they are clearly duplicates
- keep one canonical entity record
- preserve quality flags
- keep unresolved relationships visible
- give the analysis one consistent source of truth

---

# 15. Quality Issues That Matter Most

If I had to reduce the whole quality review to a few points, these would be the most important:

| Issue | Why I Care About It |
|---|---|
| Duplicate payments | Can directly overstate recovery |
| Borrower conflicts | Can affect customer-level analysis |
| Unresolved borrower links | Can affect joins and segmentation |
| Missing call agents | Makes agent attribution incomplete |
| Duplicate calls | Can inflate collection activity |
| Multiple timezones | Can affect event dates/hours |
| Multi-touch attribution | Makes channel impact difficult to isolate |

Not every data issue has the same business impact.

I gave the most attention to issues that could actually change the recovery conclusion.

---

# 16. Decisions I Made During Cleaning

A few decisions were especially important:

### I kept unresolved records when the underlying event was still useful

For example, I kept calls with missing agents rather than deleting the calls completely.

### I did not guess missing relationships

When an account could not confidently be linked to a borrower, I left it unresolved.

### I did not treat open PTPs as failures

Some promises had not matured yet.

### I did not use raw payment totals

Payment duplicates materially changed the reported recovery.

### I separated attribution from causality

A payment occurring after a collection interaction does not automatically mean the interaction caused the payment.

These choices were made to keep the analysis conservative rather than artificially improve the numbers.

---

# 17. Overall Assessment

I would describe the data as:

**Usable after cleaning, but not safe to use directly from the raw tables for executive reporting.**

The biggest concern is not the presence of a few missing values.

The bigger issue is that repeated records and inconsistent identifiers can change the business numbers if they are not handled first.

The Golden Dataset addresses the main problems while preserving enough information to audit the original records.

---

# 18. Final Takeaway

The main lesson from the data-quality work is simple:

> **Cleaning the data changed the answer.**

The raw successful payment amount was about **₹134.15 Cr**, while the canonical Golden amount was about **₹131.56 Cr**.

At the same time, the February-to-March recovery increase of **11.03%** looks less impressive once recovery is normalized by the eligible portfolio.

So I would not present the raw headline number on its own.

The final analysis is based on:

**Canonical data + correct denominators + transparent attribution + visible quality limitations**

That gives me a much more reliable basis for the investment recommendation.