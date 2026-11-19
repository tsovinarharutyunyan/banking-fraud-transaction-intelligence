# Tableau dashboards — published workbook

[Explore the three interactive dashboards on Tableau Public](https://public.tableau.com/app/profile/tsovinar.harutyunyan/viz/BankingFraudTransactionIntelligence/01-ExecutiveOverview)

This project uses the **first 300,000 records** of the synthetic PaySim dataset, not a random sample. Transaction amounts are in dataset units. Time is simulated.

## 01 — Executive Overview
Five KPI tiles: total transactions, transaction volume, labeled fraud transactions, labeled fraud rate, and average amount. Charts compare transaction counts, labeled fraud, and amount by transaction type.

## 02 — Fraud & Risk Monitoring
KPIs: rule-alert transactions, rule-alert rate, and labeled fraud transactions. Charts: alerts by type, alert activity by simulated hour and type, transactions by risk tier, and risk-score distribution.

## 03 — Transaction Intelligence
Charts: transaction mix by type (pie), amount versus risk score (scatter), and amount distribution (histogram filtered to amounts ≤ 1,000,000 dataset units).

## Interpretation
Select a transaction type in a dashboard to filter related views. The PaySim `isFraud` field is a simulated label; `isFlaggedFraud` is PaySim's existing flag; `rule_alert` is this project's separate illustrative alert. An alert is **not** confirmed fraud. The alert rule has about 48.1% recall in this extract, with a 37.33% alert rate, and is not operationally validated.

## Export and source consistency
The current Tableau dashboard uses the main `tableau/transactions_dashboard.csv` extract. The other five CSV exports are supplementary summaries and dimension tables; they are **not required as separate data sources** for these three pages. When updating the packaged workbook, edit the existing connection rather than replacing worksheets.

## Rebuild
1. Download PaySim using the dataset link in `README.md`.
2. Run `Banking_Fraud_Intelligence.ipynb` from the repository root or run `python src/analysis.py --input data/PS_20174392719_1491204439457_log.csv --limit 300000`.
3. Connect Tableau to the generated `tableau/transactions_dashboard.csv`.
4. Refer to the published Tableau workbook and the three PNG previews for the final dashboard layout.

The original exploratory design notes have been replaced by this summary of the finished workbook.
