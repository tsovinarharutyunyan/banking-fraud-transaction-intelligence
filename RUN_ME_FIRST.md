# Start here — Mac / Jupyter / Tableau

1. Download PaySim from https://www.kaggle.com/datasets/ealaxi/paysim1.
2. Keep `PS_20174392719_1491204439457_log.csv` in `~/Downloads` OR copy it to this project's `data/` directory.
3. Open `Banking_Fraud_Intelligence.ipynb` with Jupyter, from this project's directory.
4. Run **Kernel → Restart & Run All**. The default is real PaySim, first **300,000 rows** for memory safety.
5. Verify the `Source:` printout contains `PaySim dataset`, not `DEMO`.
6. Open Tableau Desktop → Connect → Text file → `tableau/transactions_dashboard.csv`.
7. Build the 3 dashboard pages with `TABLEAU_BUILD_GUIDE.md`. Save as `.twbx` and publish to Tableau Public only after checking KPI values.

**Do not upload the original PaySim CSV to GitHub.** `data/*.csv` is gitignored. The dataset is synthetic, and risk alerts are illustrative rules rather than confirmed real fraud.
