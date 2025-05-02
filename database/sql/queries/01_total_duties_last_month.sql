-- Total duties collected last month
SELECT
  SUM(p.amount) AS total_collected_last_month
FROM payments p
WHERE p.status = 'completed'
  AND p.paid_at >= (date_trunc('month', CURRENT_DATE) - INTERVAL '1 month')
  AND p.paid_at <  date_trunc('month', CURRENT_DATE);
