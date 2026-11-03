SELECT nameOrig AS account_id, COUNT(*) AS transactions,
 ROUND(SUM(amount),2) AS total_amount, SUM(rule_alert) AS alerts
FROM transactions GROUP BY nameOrig HAVING COUNT(*) >= 5
ORDER BY transactions DESC LIMIT 100;
