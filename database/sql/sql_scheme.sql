-- 1. Enum types
CREATE TYPE user_role AS ENUM ('importer','admin');
CREATE TYPE declaration_status AS ENUM ('draft','submitted','paid');
CREATE TYPE payment_status AS ENUM ('pending','completed','failed');

-- 2. Tables

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  company VARCHAR(255) NOT NULL,
  role user_role NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE countries (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  iso_code CHAR(2) NOT NULL UNIQUE
);

CREATE TABLE product_categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  hs_code VARCHAR(10),
  category_id INT NOT NULL REFERENCES product_categories(id),
  country_id INT NOT NULL REFERENCES countries(id)
);

CREATE TABLE tariff_rates (
  id SERIAL PRIMARY KEY,
  country_id INT NOT NULL REFERENCES countries(id),
  category_id INT NOT NULL REFERENCES product_categories(id),
  rate_value NUMERIC(5,2) NOT NULL,
  effective_from DATE NOT NULL
);

CREATE TABLE import_declarations (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  product_id INT NOT NULL REFERENCES products(id),
  quantity INT NOT NULL,
  unit_cost NUMERIC(12,2) NOT NULL,
  status declaration_status NOT NULL,
  declaration_date DATE NOT NULL
);

CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  declaration_id INT NOT NULL REFERENCES import_declarations(id),
  amount NUMERIC(12,2) NOT NULL,
  status payment_status NOT NULL,
  paid_at TIMESTAMP
);