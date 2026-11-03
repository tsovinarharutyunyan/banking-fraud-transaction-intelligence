-- Required INNER JOIN: transactions to type dimension
SELECT tt.type, tt.type_group, COUNT(*) AS transactions,
 ROUND(SUM(t.amount),2) AS total_amount,
 SUM(t.isFraud) AS labeled_fraud, SUM(t.rule_alert) AS alerts,
 ROUND(100.0*SUM(t.isFraud)/COUNT(*),4) AS labeled_fraud_pct
FROM transactions t
INNER JOIN transaction_types tt ON t.type=tt.type
GROUP BY tt.type,tt.type_group ORDER BY transactions DESC;
