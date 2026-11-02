# Banking Fraud & Transaction Intelligence

**Python · Pandas · SQL (SQLite) · Tableau**

I built this project to explore how transaction data can support day-to-day fraud and risk monitoring. The focus is on understanding transaction patterns, testing simple and explainable alert rules, and presenting the findings in dashboards that are easy to investigate.

**[Explore the interactive Tableau dashboards](https://public.tableau.com/app/profile/tsovinar.harutyunyan/viz/BankingFraudTransactionIntelligence/03-TransactionIntelligence)**

## The data

The analysis uses **300,000 transactions** from the beginning of the [PaySim synthetic financial transactions dataset](https://www.kaggle.com/datasets/ealaxi/paysim1). PaySim simulates mobile-money activity; it does not contain real bank customers or transactions.

I used a limited extract to keep the notebook and Tableau workbook manageable on a laptop. **This is the first 300,000 rows, not a random or representative sample.** All figures below describe this extract only. Transaction amounts are reported in *dataset units*, not a claimed real-world currency.

## What I found

| Metric | Result |
|---|---:|
| Transactions analyzed | 300,000 |
| Total transaction amount | 52.85B dataset units |
| Transactions labeled as fraud | 181 |
| Labeled fraud rate | 0.0603% |
| Rule-based alerts | 112,004 |
| Alert rate | 37.33% |

Fraud labels appear only in **CASH_OUT** (93) and **TRANSFER** (88) transactions in this extract. These are observations from simulated data, not evidence that other transaction types are fraud-free in real banking.

The alert rules flagged **87 of the 181** labeled fraud cases, or approximately **48.1% recall**. They also flagged **111,917 transactions without a fraud label**. This is an intentionally simple monitoring example, **not a validated fraud-detection model**. Its alert volume would be far too broad to treat as an operationally ready fraud queue.

## Interactive dashboards

The Tableau workbook contains three views:

1. **Executive Overview** — transaction counts, total amount, fraud KPIs, and activity by transaction type.
2. **Fraud & Risk Monitoring** — rule alerts, risk tiers, score distribution, and alert patterns by hour and transaction type.
3. **Transaction Intelligence** — transaction mix, the relationship between amount and risk score, and the distribution of transaction amounts (with the histogram limited to amounts up to 1M).

Charts can be selected to filter other views within each dashboard. The published workbook is available through the link above.

## How I approached it

- **Python / Pandas:** load and check transactions, derive relative simulation day and hour, build transaction-level risk indicators, and export summaries for visualization.
- **Rule-based risk scoring:** assign 2 points for an amount of at least 100,000; add 1 point if the amount exceeds the origin account's pre-transaction balance; add 1 point for TRANSFER or CASH_OUT. Scores of 3 or more trigger a rule alert.
- **SQL / SQLite:** organize transaction and account data and explore it with joins, aggregations, CTEs, `CASE WHEN`, `HAVING`, and window functions. Seven example queries are in `sql/`.
- **Tableau:** build three interactive dashboards from the prepared transaction data.

The risk score uses only pre-transaction information for its balance check. The dataset's `isFraud` field is the simulated label; `isFlaggedFraud` is PaySim's own flag; and `rule_alert` is **my separate rule-based indicator**. They are not interchangeable.

## Repository guide

| File / folder | Purpose |
|---|---|
| `Banking_Fraud_Intelligence.ipynb` | Main notebook, with analysis and explanations |
| `src/analysis.py` | Reusable Python analysis pipeline |
| `sql/` | Seven SQL analysis queries |
| `requirements.txt` | Python dependencies |
| `RUN_ME_FIRST.md` | Setup instructions |
| `TABLEAU_BUILD_GUIDE.md` | Notes on the Tableau dashboard build |
| `RESULTS.md` | Output from the last pipeline run; check its dataset label before comparing figures |
| `tableau/`, `outputs/` | Generated exports and results, if included |

## Run it locally

1. Download the PaySim CSV from the dataset link above and place it in a local `data/` folder.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Open `Banking_Fraud_Intelligence.ipynb` and run it from the project folder, or run the script:

   ```bash
   python src/analysis.py --input "data/PS_20174392719_1491204439457_log.csv" --limit 300000
   ```

4. Open the generated Tableau exports in Tableau Desktop, or explore the published dashboards above.

For a quick run without downloading PaySim, the script also supports `python src/analysis.py --demo`. **Demo results are generated examples and should not be compared with the PaySim figures above.**

## Limitations

- The dataset is synthetic, and the sample is a nonrandom slice of the original file.
- PaySim's `step` is a simulated hour, not a calendar date. This extract covers only one derived simulation day, so it cannot support a meaningful day-over-day trend.
- Risk thresholds are illustrative; they have not been tuned, calibrated, or tested for production use.
- A rule alert is not a confirmed fraud case, and an account identifier is not necessarily a unique individual.
- The analysis is a portfolio exercise in transaction monitoring and communication, not a live banking system.

**Data source:** [PaySim — Synthetic Financial Datasets for Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1)
