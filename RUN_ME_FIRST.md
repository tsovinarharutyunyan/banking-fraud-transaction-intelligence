# Start here — Mac / Jupyter / Tableau

1. Download PaySim from https://www.kaggle.com/datasets/ealaxi/paysim1.
2. Keep `PS_20174392719_1491204439457_log.csv` in `~/Downloads` OR copy it to this project's `data/` directory.
3. Open `Banking_Fraud_Intelligence.ipynb` with Jupyter, from this project's directory.
4. Run **Kernel → Restart & Run All**. The default is real PaySim, first **300,000 rows** for memory safety.
5. Verify the `Source:` printout contains `PaySim dataset`, not `DEMO`.
6. Open Tableau Desktop → Connect → Text file → `tableau/transactions_dashboard.csv`.
7. To view the finished dashboards, open the [published Tableau workbook](https://public.tableau.com/app/profile/tsovinar.harutyunyan/viz/BankingFraudTransactionIntelligence/01-ExecutiveOverview). If updating a local Tableau workbook, use **Edit Connection** to point its existing `transactions_dashboard` data source to the new CSV; keep its original field names and confirm KPI values before saving as `.twbx`.

**Do not upload the original PaySim CSV to GitHub.** `data/*.csv` is gitignored. The dataset is synthetic, and risk alerts are illustrative rules rather than confirmed real fraud.
