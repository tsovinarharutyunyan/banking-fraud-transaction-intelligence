# Tableau Dashboard Blueprint — Banking Fraud & Transaction Intelligence

## Data connection

Connect Tableau Public/Desktop to `tableau/transactions_dashboard.csv` after running the Python pipeline. `day` is a **simulation day**, `hour` is a **simulation hour**, and `amount` is in **dataset units**, not USD. The fact CSV already contains the fields needed for all three dashboards. Optional `accounts.csv` and `transaction_types.csv` can be related by account/type if desired; avoid many-to-many row duplication.

## Calculated fields

Create:

- `Fraud Rate` = `SUM([isFraud]) / COUNT([transaction_id])`
- `Alert Rate` = `SUM([rule_alert]) / COUNT([transaction_id])`
- `Fraudulent Volume` = `SUM(IF [isFraud] = 1 THEN [amount] ELSE 0 END)`
- `Alerted Volume` = `SUM(IF [rule_alert] = 1 THEN [amount] ELSE 0 END)`
- `Avg Transaction` = `AVG([amount])`
- `Alert Precision` = `SUM(IF [rule_alert]=1 AND [isFraud]=1 THEN 1 ELSE 0 END) / MAX(1,SUM([rule_alert]))`
- `Alert Recall` = `SUM(IF [rule_alert]=1 AND [isFraud]=1 THEN 1 ELSE 0 END) / MAX(1,SUM([isFraud]))`

Display rates as percentages. Note Tableau formula syntax may need exact field typing adjustments.

## Dashboard 1: Executive Transaction Overview (1200 × 800)

**Header:** Banking Transaction Intelligence | Simulated Data

**KPI cards:** Transactions = COUNT([transaction_id]); Total Volume = SUM([amount]); Average Transaction = AVG([amount]); Labeled Fraud = SUM([isFraud]); Labeled Fraud Rate = calculated field.

**Sheet A:** line chart: Columns `day`, Rows COUNT(transaction_id). `day` is discrete simulation day.

**Sheet B:** horizontal bar: Rows `type`, Columns SUM(amount); sort descending.

**Sheet C:** bar: Rows `amount_band`, Columns COUNT(transaction_id); sort bins logically.

**Sheet D:** transaction-type breakdown table: type, count, volume, labeled fraud, rate.

**Filters:** type, day, amount_band. Apply to all relevant worksheets using this source.

## Dashboard 2: Fraud & Risk Monitoring (1200 × 800)

**KPI cards:** Rule Alerts, Alert Rate, Labeled Fraud, Alert Precision, Alert Recall.

**Sheet A:** heatmap: Columns hour, Rows day, Color SUM(rule_alert); show simulation time explicitly.

**Sheet B:** bar: risk_tier vs COUNT(transaction_id); ordered Low, Medium, High.

**Sheet C:** side-by-side bars: type vs SUM(rule_alert) and SUM(isFraud). Make clear these are different quantities.

**Sheet D:** alert review table: transaction_id, type, amount, risk_score, risk_tier, rule_alert, isFraud. Filter rule_alert = 1 by default.

**Filters:** day, type, risk_tier, rule_alert. Use consistent dashboard actions.

## Dashboard 3: Account & Transaction Intelligence (1200 × 800)

**KPI cards:** Distinct Origin Accounts = COUNTD([nameOrig]); Distinct Destination Accounts = COUNTD([nameDest]); Average Transaction; Alerted Volume.

**Sheet A:** top 15 origin accounts by SUM(amount), sorted descending.

**Sheet B:** scatter: each nameOrig, x COUNT(transaction_id), y SUM(amount), size SUM(rule_alert). Beware overplotting; filter top accounts.

**Sheet C:** transaction distribution by amount_band and type, stacked bars.

**Sheet D:** detail table: transaction_id, nameOrig, nameDest, type, amount, day, hour, risk_tier.

**Filters:** day, type, risk_tier. Add highlight action from top-account bar to transaction detail.

## Visual quality checklist

- Use a restrained navy, white and teal palette; reserve amber/red for flagged-risk indicators.
- Keep 4–5 KPI cards on top; 2-column chart grid below; filter rail on right.
- Provide informative tooltips and source note: “Synthetic PaySim or illustrative demo; no real customer data.”
- Use dashboard navigation buttons between the three views.
- Add methodology and definitions in tooltip/footer; do not call alerts proven fraud.
- Validate all KPI totals against `outputs/summary.json` and `tableau/daily_metrics.csv`.

## Publishing

Tableau Public → connect to CSV → create sheets → assemble dashboards → File → Save to Tableau Public. Publish only synthetic data and never personal customer information. Add your actual Tableau Public link to README after publishing.
