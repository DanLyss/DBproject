-- Average tariff rate per product category
SELECT
  pc.name              AS category,
  ROUND(AVG(tr.rate_value), 2) AS avg_rate_percent
FROM tariff_rates tr
JOIN product_categories pc ON tr.category_id = pc.id
GROUP BY pc.name
ORDER BY avg_rate_percent DESC;
