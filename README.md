# DBproject / TradeTariffManager

A local prototype of **TradeTariffManager**—a system for calculating, tracking and paying import tariffs on goods.

---

## 1. Domain Description

**TradeTariffManager** lets importers look up current duty rates by _country_ & _product category_, create an **ImportDeclaration** (quantity, cost, date), have the system calculate duties, pay online, and track status. Admins manage **TariffRate** entries and view collections reports.

> To reconstruct the schema, one must know:
> - Countries (ISO codes) & product categories  
> - Products belong to a single category & origin country (HS code)  
> - Tariff rates per (country, category) pair with a rate and effective date  
> - Users (importer/admin)  
> - ImportDeclaration ties user⇄product with qty, cost, status & date  
> - Payment links to declaration with amount, status & timestamp

---

## 2. Entities & Relationships

| Entity                 | Key Fields & FKs                                                                 |
|------------------------|----------------------------------------------------------------------------------|
| **Users**              | `id` PK, `email` UNIQUE NOT NULL, `company` NOT NULL, `role` (importer/admin), `created_at` |
| **Country**            | `id` PK, `name` NOT NULL, `iso_code` CHAR(2) NOT NULL UNIQUE                     |
| **ProductCategories**  | `id` PK, `name` NOT NULL                                                         |
| **Products**           | `id` PK, `name` NOT NULL, `hs_code` VARCHAR, `category_id` → ProductCategory.id, `country_id` → Country.id |
| **TariffRates**        | `id` PK, `country_id` → Country.id, `category_id` → ProductCategory.id, `rate_value` NUMERIC, `effective_from` DATE |
| **ImportDeclarations** | `id` PK, `user_id` → User.id, `product_id` → Product.id, `quantity` INT, `unit_cost` NUMERIC, `status` ENUM, `declaration_date` DATE |
| **Payments**           | `id` PK, `declaration_id` → ImportDeclaration.id, `amount` NUMERIC, `status` ENUM, `paid_at` TIMESTAMP |

---

## 3. Critical User Scenarios

1. **Lookup Tariff Rate**  
   - Importer selects country + category → system queries latest **TariffRate** → displays %.

2. **Create & Submit Declaration**  
   - Importer enters product, quantity, unit cost → system computes  
     `duty = unit_cost × quantity × (rate_value / 100)` → saves **ImportDeclaration** with `status='submitted'`.

3. **Pay Duties**  
   - Importer pays a submitted declaration → creates **Payment**(`status='pending'`); on payment callback updates to `completed` and declaration→`paid`.

4. **Admin Updates Tariff**  
   - Admin inserts new **TariffRate** for (country,category) → effective for future declarations.

5. **View Collections Dashboard**  
   - Admin aggregates **Payment.amount** by month/category (`GROUP BY`) → displays totals & top categories.

---

## 4. Database Schema & Diagram

- [**DDL (PostgreSQL)**:](./sql/sql_scheme.sql)  
- [**DBML**:](./dbml/dbml_scheme.dbml)  
- [**ER Diagram**:](./scheme_image.pdf)

---


## 5. Fake Data / Seeding

  - **Static SQL**:  
  ```bash
  psql -h localhost -U postgres -d mydb -f sql/seed.sql
   ```
  - **Dynamic Faker (recommended):**

  ```bash
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  python DBproject/scripts/seed.py
  ```

  Connection credentials are loaded from `.env`.

---

## 6. Analytical Queries

**Query files:**

| File                                                    | Purpose                                       |
|---------------------------------------------------------|-----------------------------------------------|
| `sql/queries/01_total_duties_last_month.sql`            | Total duties collected last month             |
| `sql/queries/02_top5_countries_by_declarations.sql`     | Top 5 origin countries by declaration count   |
| `sql/queries/03_avg_tariff_per_category.sql`            | Average tariff rate per product category      |

**Example usage:**

```bash
psql -h localhost -U postgres -d mydb -f sql/queries/01_total_duties_last_month.sql
```

---

## 7. Indexes & Optimization

[**Recommended indexes**](./sql/indexes.sql)
---
### ▶ Applying Indexes and Measuring Query Performance

You can verify how indexes improve real query performance by using your existing `.sql` files with `\timing`.

---

#### 🧱 Step 1: Apply indexes

Run this once to create all performance-boosting indexes:

```bash
psql -h localhost -U postgres -d mydb -f sql/indexes.sql
```

---

#### ⏱ Step 2: Measure execution time of real queries

1. Start the interactive Postgres shell:

```bash
psql -h localhost -U postgres -d mydb
```

2. Inside the shell, enable timing:

```sql
\timing
```

3. Run any of the project queries from the `sql/queries/` folder. For example:

```sql
\i sql/queries/02_top5_countries_by_declarations.sql
```

4. You’ll see output like:

```
    country    | declarations_count
---------------+--------------------
 United States |                 51
 Brazil        |                 51
 China         |                 39
 Germany       |                 30
 Japan         |                 29
(5 rows)

Time: 4,458 ms
```
5. While when running without indexes would get you
```
    country    | declarations_count
---------------+--------------------
 United States |                 51
 Brazil        |                 51
 China         |                 39
 Germany       |                 30
 Japan         |                 29
(5 rows)

Time: 94,412 ms
```
---

Signinficant improvement in performance.
This method works for all analytical query files:

```bash
sql/queries/01_total_duties_last_month.sql
sql/queries/02_top5_countries_by_declarations.sql
sql/queries/03_avg_tariff_per_category.sql
```

---

---

## 8. Quick Start (Local)

```bash
# 1. Activate virtualenv
.\.venv\Scripts\Activate.ps1

# 2. Install requirements
pip install -r requirements.txt

# 3. Create DB
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE mydb;"

# 4. Load schema
psql -h localhost -U postgres -d mydb -f DBproject/sql/sql_scheme.sql

# 5. Seed data
python DBproject/scripts/seed.py

# 6. Run a query
psql -h localhost -U postgres -d mydb -f DBproject/sql/queries/01_total_duties_last_month.sql
```

---

## 🐧 Bonus: Sanctioned Penguins Example

To demonstrate a custom use case, we simulate a scenario where "Frozen Penguins" imported from Heard Island and McDonald Islands are now subject to a 40% tariff.

Run the following script to insert:

- A new country: `Heard Island and McDonald Islands`
- A new product category: `Penguins`
- A product: `Frozen Penguin`
- A 40% tariff for that category from that country
- A sample declaration and payment by one importer

```bash
psql -h localhost -U postgres -d mydb -f sql/scripts/add_penguin_sanction.sql

