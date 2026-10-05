# Strategy Note: Where to Focus Distribution Effort

**Scope:** 381,109 cross-sell leads, 34 channels (500+ leads), 53 regions. Overall conversion: 12.26%.

## 1. Stop spending sales effort on customers who already hold cover
**Finding:** Customers with prior insurance are 45.8% of leads (174,628) but converted at 0.09%, which is 158 conversions, about 0.3% of the total. Customers with no prior insurance and past vehicle damage are 47.9% of leads (182,491), converted at 25.01% and produced 97.7% of all conversions.

**Action:** Add a lead-qualification rule that routes prior-insured customers out of the active calling list, and prioritise uninsured customers with past vehicle damage. Use the lead-scoring model (AUC 0.836) to rank the rest.

**Expected impact:** The top-scoring 10% of leads converts at 34.9% against a 12.3% base, a 2.9x lift. Sales time freed from low-yield leads can be redirected to this pool.

## 2. Fix the six high-volume, low-conversion channels
**Finding:** Six of 34 channels are in the "Fix" tier. They hold 44.1% of leads in analysed channels but convert below the median.

**Action:** Review incentive structures so they reward conversion and not only volume, and give those channels coaching and lead-quality support. Use `outputs/channel_tiers.csv` for the channel list. Route extra leads to the six "Scale-up" channels, which convert above the median on lower volume, and protect the eleven "Star" channels.

**Expected impact:** Moving even part of the "Fix" group toward the median conversion rate lifts overall conversion, because these channels carry a large share of lead volume.

## 3. Target the highest-uplift under-converting regions
**Finding:** 36 regions with 1,000+ leads convert below the top-quartile benchmark of 12.18%. Reaching it is worth an estimated 199.6M premium units, or 99.8M if only half the gap closes. Regions 8, 15 and 50 account for 70.0M, about 35% of the total.

**Action:** Start a territory activation programme in regions 8, 15 and 50 (local sales coaching, channel mix review), then extend to the next regions in `outputs/region_whitespace.csv`.

**Expected impact:** 31.7M (region 8), 19.6M (region 15) and 18.7M (region 50) in estimated premium if each reaches the benchmark.

## 4. Rebalance the age and vehicle-age mix
**Finding:** Ages 18-25 are 30.0% of leads but convert at 3.53% and give 8.7% of conversions. Ages 36-55 give 58.5% of conversions. Vehicles older than 2 years convert at 29.37% but are only 4.2% of leads.

**Action:** Shift outreach toward ages 36-55 and test cheaper, lower-touch channels for ages 18-25. Expand lead sourcing for customers with older vehicles.

**Expected impact:** More conversions per sales hour from the same lead budget, and a larger pool in the highest-converting vehicle segment.

## Caveats
- These are associations and sizing estimates, not causal forecasts, and they ignore cost, margin and sales capacity.
- Channel and region codes are anonymised. With named agent and broker data, the same method would support partner-level programmes.
- Conversion differs by gender in the data, but it should not be used as a targeting criterion.
