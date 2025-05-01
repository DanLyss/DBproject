-- Add "Heard Island and McDonald Islands" as a country (ISO code HM)
INSERT INTO countries (name, iso_code)
VALUES ('Heard Island and McDonald Islands', 'HM')
ON CONFLICT (iso_code) DO NOTHING;

-- Add "Penguins" category
INSERT INTO product_categories (name)
SELECT 'Penguins'
WHERE NOT EXISTS (
  SELECT 1 FROM product_categories WHERE name = 'Penguins'
);

-- Build everything using CTEs
WITH
  co AS (
    SELECT id AS country_id FROM countries WHERE iso_code = 'HM'
  ),
  cat AS (
    SELECT id AS category_id FROM product_categories WHERE name = 'Penguins'
  ),
  prod AS (
    INSERT INTO products (name, hs_code, category_id, country_id)
    SELECT 'Frozen Penguin', '999999', cat.category_id, co.country_id
    FROM co, cat
    RETURNING id AS product_id
  ),
  tariff AS (
    INSERT INTO tariff_rates (country_id, category_id, rate_value, effective_from)
    SELECT co.country_id, cat.category_id, 40.00, CURRENT_DATE
    FROM co, cat
  ),
  importer AS (
    SELECT id AS user_id FROM users WHERE role = 'importer' LIMIT 1
  ),
  decl AS (
    INSERT INTO import_declarations (user_id, product_id, quantity, unit_cost, status, declaration_date)
    SELECT importer.user_id, prod.product_id, 10, 100.00, 'paid', CURRENT_DATE
    FROM importer, prod
    RETURNING id AS declaration_id
  )
INSERT INTO payments (declaration_id, amount, status, paid_at)
SELECT decl.declaration_id, 10 * 100.00 * 0.40, 'completed', now()
FROM decl;
