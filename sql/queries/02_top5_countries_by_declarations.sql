-- Top 5 countries by number of import declarations
SELECT
  c.name                AS country,
  COUNT(d.id)           AS declarations_count
FROM import_declarations d
JOIN products p  ON d.product_id = p.id
JOIN countries c ON p.country_id  = c.id
GROUP BY c.name
ORDER BY declarations_count DESC
LIMIT 5;
