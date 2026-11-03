SELECT CASE WHEN risk_score>=3 THEN 'High'
 WHEN risk_score>=1 THEN 'Medium' ELSE 'Low' END AS risk_segment,
 COUNT(*) AS transactions, SUM(isFraud) AS labeled_fraud,
 ROUND(100.0*SUM(isFraud)/COUNT(*),4) AS labeled_fraud_pct
FROM transactions GROUP BY risk_segment
ORDER BY CASE risk_segment WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;
