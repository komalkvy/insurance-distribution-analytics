# Insurance Distribution Growth Analytics

Channel performance, partner segmentation and white-space analysis on 381,109 insurance cross-sell leads.

## Business problem
A distribution team needs to know where to spend sales effort. This project answers four questions:
1. Which customer segments actually convert, and which waste effort?
2. Which sales channels (a stand-in for agents and brokers) should be protected, scaled, fixed or reviewed?
3. Which regions are under-converting, and what is the size of the opportunity?
4. Can leads be ranked by likelihood to convert?

## Data
Kaggle: *Health Insurance Cross Sell Prediction* (`train.csv`). Health insurance customers were contacted to cross-sell vehicle insurance. `response = 1` means the customer was interested, which is treated as a conversion.

- 381,109 leads, 12 columns, no missing values, no duplicate ids
- Region and sales-channel values are anonymised codes, not names
- The dataset does not state a currency, so premium figures are in dataset units

## Approach
1. **Clean and load.** Removed duplicate ids, created age bands, loaded the data into SQLite (`insurance_analysis.py`).
2. **Conversion analysis in SQL.** Conversion by age band, vehicle age, vehicle damage, prior insurance, gender, region and channel (`sql/queries.sql`).
3. **Channel tiering.** For the 34 channels with 500+ leads, split at the median lead volume and median conversion rate into four tiers: Star, Scale-up, Fix and Review, each with a suggested action.
4. **White-space sizing.** Benchmarked each region against the top-quartile conversion rate (12.18%, among regions with 1,000+ leads). Estimated extra conversions if a region reached the benchmark, multiplied by its average premium. A conservative case closes half the gap.
5. **Lead-scoring model.** Logistic regression on customer attributes (75/25 stratified split) to rank leads by conversion likelihood.

## Key findings
- Overall conversion is **12.26%** (46,710 of 381,109 leads).
- Customers who already had insurance (45.8% of leads) converted at **0.09%**.
- Customers with no prior insurance and past vehicle damage (47.9% of leads) converted at **25.01%** and produced **97.7%** of all conversions.
- Ages 18-25 are the largest age group (30.0% of leads) but convert at **3.53%**, against **21.54%** for ages 36-45.
- Vehicles older than 2 years convert at **29.37%**, but are only 4.2% of leads.
- Of 34 channels, 6 are **Fix** channels. They hold **44.1%** of leads in analysed channels but convert below the median.
- 36 regions with 1,000+ leads are below the benchmark. Closing the gap is worth an estimated **199.6M** premium units (**99.8M** conservative). Regions 8, 15 and 50 account for about 35% of that.
- The lead-scoring model reaches **AUC 0.836**. Its top decile converts at **34.9%** against a 12.3% base (2.9x lift).

Charts are in `outputs/charts/`. Full numbers are in `outputs/findings.txt`. Recommendations are in `docs/strategy_note.md`.

## Limitations
- Associations, not causes. The segments that convert best are not proven to be the reason they convert.
- Channel and region codes are anonymised, so the "partner" analysis uses channel codes. The same method applies to named agents and brokers.
- No cost, margin or capacity data, so the uplift is a sizing estimate and not a forecast.
- Gender shows a conversion gap, but the project does not recommend targeting by gender.

## Run it
```
pip install -r requirements.txt
# put train.csv in data/
python insurance_analysis.py --model
```
Outputs are written to `outputs/`.

## Files
- `insurance_analysis.py`: full pipeline (cleaning, SQL, tiering, white-space, model, charts)
- `sql/queries.sql`: all SQL queries
- `outputs/`: result tables, channel tiers, region white-space, charts, findings
- `docs/strategy_note.md`: recommendations for leadership
