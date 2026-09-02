# Executive Memo

## Collections Performance Review

### To: Leadership Team  
### Subject: What actually happened to recovery, and where I would put the next ₹10 Cr

---

## My Recommendation

I would invest the next **₹10 Cr in better borrower targeting**, but I would **not release the entire amount upfront**.

I would start with a controlled pilot where borrowers are split into a treatment group and a comparable control group. The investment should scale only if the new targeting approach produces measurable incremental recovery over the control group.

The reason for this cautious recommendation is that the data does show a recovery improvement, but it does **not** prove that the operational change caused it.

---

# 1. What Happened?

The headline number is true in one narrow sense:

**Gross recovery increased 11.03% from February to March.**

However, that is not the full story.

The eligible portfolio also increased during the period. When I normalize recovery by eligible accounts, the picture changes:

**Recovery per eligible account fell 18.37%.**

So I would describe the situation as:

> **Recovery increased in absolute terms, but recovery efficiency did not improve at the same rate.**

March also had higher collection activity and PTP creation, while the overall portfolio mix remained broadly stable.

### My classification

**11.03% gross recovery increase → FACT**

**18.37% decline in recovery per eligible account → FACT**

**Higher activity alongside higher gross recovery → STRONG EVIDENCE**

**A specific channel or strategy caused the increase → NOT ESTABLISHED**

---

# 2. What Made Me Less Confident in the Headline?

The raw data has several issues that materially affect the analysis.

The biggest one was payments.

There are **25,500 raw payment rows but only 25,000 unique payment IDs**. After resolving repeated payment records, successful recovery changed from approximately:

**₹134.15 Cr → ₹131.56 Cr**

That is a difference of roughly:

**₹2.59 Cr**

So I would not use the raw payment table for executive recovery reporting.

I also found **8,518 borrower IDs with conflicting attributes**, **2,913 unresolved account-to-borrower relationships**, and **1,827 calls with missing agent IDs**.

These issues do not make the entire dataset unusable, but they do make some borrower-level and agent-level conclusions less certain.

---

# 3. What About Channels?

This is where I would be careful.

A successful payment can happen after multiple collection interactions.

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

So assigning the payment entirely to the last channel touched can make that channel look better than it actually was.

I tested 7-day, 14-day and 30-day attribution windows.

In the 30-day latest-touch view, approximately **40% of successful recovery value had no prior interaction under the attribution definition**.

That makes it difficult to say:

> “Channel X generated ₹Y of incremental recovery.”

The data supports channel association, but not channel causation.

---

# 4. Why I Prefer Targeting for the ₹10 Cr Investment

The data does not give me strong enough evidence to confidently say that telephony, more agents, WhatsApp, field visits, or another channel is the clear winner.

Targeting is different because it directly addresses the question:

> **Which borrowers should receive collection effort, and when?**

The existing data already contains useful targeting variables such as:

- DPD
- Risk segment
- Loan type
- Outstanding amount
- Prior collection activity
- Historical recovery
- Contact history

That makes targeting a practical area to test.

But I want to be clear:

> **I am recommending targeting as the area to test, not claiming that targeting has already been proven causal.**

---

# 5. How I Would Deploy the ₹10 Cr

I would use a controlled rollout.

### Treatment

Borrowers/accounts selected using the improved targeting strategy.

### Control

Comparable accounts continuing under the existing targeting approach.

The two groups should be balanced using pre-treatment characteristics such as DPD, risk, loan type, outstanding amount, previous collection activity and historical recovery.

The primary KPI would be:

**Incremental recovery per eligible account**

I would also track:

- Contact rate
- PTP rate
- PTP kept rate
- Recovery per agent-hour
- Cost per ₹ recovered

A Difference-in-Differences analysis can be used where historical pre-treatment trends are available.

---

# 6. Financial View

Using the current recovery base, the investment scenarios are approximately:

| Scenario | Assumed Uplift | Incremental Recovery | Net Value | ROI |
|---|---:|---:|---:|---:|
| Downside | 2% | ₹4.35 Cr | -₹5.65 Cr | -56.51% |
| Base Case | 5% | ₹10.87 Cr | ₹0.87 Cr | 8.73% |
| Upside | 10% | ₹21.75 Cr | ₹11.75 Cr | 117.45% |

The approximate **break-even uplift is 4.6%**.

In other words, the investment needs to generate roughly a **4.6% incremental recovery improvement** against the appropriate control/baseline to recover the ₹10 Cr investment.

### Important assumption

These scenarios are decision scenarios, not observed causal results.

The current data does not prove that a 5% uplift will happen.

The actual investment decision should therefore be based on measured incremental recovery from the pilot.

---

# 7. Confidence Level

My confidence is:

### High confidence

- Gross recovery increased 11.03% from February to March.
- Recovery per eligible account declined 18.37%.
- Payment duplicates materially affect reported recovery.
- Portfolio mix was broadly stable.
- Payment attribution is multi-touch.

### Medium confidence

- Increased operational activity contributed to the recovery movement.
- The targeting opportunity is commercially attractive.

### Low confidence

- A specific channel caused the recovery improvement.
- The current data can support a reliable causal ROI estimate without an experiment.

---

# 8. What I Would Do Next

I would not make the decision:

> “Recovery went up 11%, so spend ₹10 Cr.”

I would make it:

> **“There is enough evidence to test better targeting, but not enough evidence to claim the full ₹10 Cr will generate a positive return.”**

The first stage should therefore be a controlled pilot with predefined success criteria.

I would scale the investment only if the treatment group shows:

1. Positive incremental recovery versus control
2. Improvement in recovery per eligible account
3. Acceptable cost per ₹ recovered
4. No deterioration in customer or operational metrics
5. Stable data quality and attribution coverage

---

# Final Decision

**Recommended investment area: Better Borrower Targeting**

**Recommended approach: Controlled pilot → measure incremental impact → scale only if the economics hold.**

The most important conclusion from this analysis is that the **11.03% headline is not false, but it is incomplete**.

The stronger decision is to move from reporting correlation to measuring incremental impact.

> **Use the ₹10 Cr to test better targeting, not to assume it works.**