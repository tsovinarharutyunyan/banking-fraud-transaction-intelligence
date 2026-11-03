WITH daily AS (
 SELECT day, COUNT(*) AS transactions, SUM(isFraud) AS labeled_fraud,
 ROUND(SUM(amount),2) AS amount FROM transactions GROUP BY day
)
SELECT day, transactions, labeled_fraud, amount,
 DENSE_RANK() OVER (ORDER BY transactions DESC) AS activity_rank,
 SUM(transactions) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS cumulative_transactions
FROM daily ORDER BY day;
