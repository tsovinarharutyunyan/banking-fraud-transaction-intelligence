SELECT SUM(CASE WHEN rule_alert=1 AND isFraud=1 THEN 1 ELSE 0 END) AS true_positive,
 SUM(CASE WHEN rule_alert=1 AND isFraud=0 THEN 1 ELSE 0 END) AS false_positive,
 SUM(CASE WHEN rule_alert=0 AND isFraud=1 THEN 1 ELSE 0 END) AS false_negative,
 SUM(CASE WHEN rule_alert=0 AND isFraud=0 THEN 1 ELSE 0 END) AS true_negative
FROM transactions;
