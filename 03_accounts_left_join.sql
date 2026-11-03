-- Required LEFT JOIN: keep all originating accounts even with no outgoing transactions
WITH origin_summary AS (
 SELECT nameOrig AS account_id, COUNT(*) AS outgoing_count,
 ROUND(SUM(amount),2) AS outgoing_amount,
 SUM(isFraud) AS labeled_fraud, SUM(rule_alert) AS alerts
 FROM transactions GROUP BY nameOrig
)
SELECT a.account_id, a.account_type,
 COALESCE(o.outgoing_count,0) AS outgoing_count,
 COALESCE(o.outgoing_amount,0) AS outgoing_amount,
 COALESCE(o.labeled_fraud,0) AS labeled_fraud,
 COALESCE(o.alerts,0) AS alerts
FROM accounts a LEFT JOIN origin_summary o ON a.account_id=o.account_id
ORDER BY outgoing_amount DESC LIMIT 1000;
