-- sql_scheme/seed.sql

-- Users
INSERT INTO users (email, company, role) VALUES
  ('alice@importco.com', 'ImportCo LLC', 'importer'),
  ('bob@tradeinc.com', 'TradeInc', 'importer'),
  ('admin@tariffmgr.io','TariffMgr','admin');

-- Countries
INSERT INTO countries (name, iso_code) VALUES
  ('United States','US'),
  ('China','CN'),
  ('Germany','DE');

-- …and so on for product_categories, products, tariff_rates, import_declarations, payments.
