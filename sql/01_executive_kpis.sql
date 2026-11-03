SELECT COUNT(*) AS transactions, ROUND(SUM(amount),2) AS total_amount,
 ROUND(AVG(amount),2) AS average_amount, SUM(isFraud) AS labeled_fraud,
 ROUND(100.0*SUM(isFraud)/COUNT(*),4) AS labeled_fraud_pct,
 SUM(rule_alert) AS rule_alerts
FROM transactions;
