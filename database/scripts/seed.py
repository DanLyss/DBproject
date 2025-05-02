# scripts/seed.py
from dotenv import load_dotenv
import os, psycopg2, random
from faker import Faker
from datetime import timedelta

# load connection params from .env
load_dotenv()
conn = psycopg2.connect(
    host     = os.getenv("POSTGRES_HOST"),
    port     = os.getenv("POSTGRES_PORT"),
    dbname   = os.getenv("POSTGRES_DB"),
    user     = os.getenv("POSTGRES_USER"),
    password = "1",
)
cur = conn.cursor()
fake = Faker()

# 1) Users: 1 admin + 50 importers
cur.execute("INSERT INTO users (email, company, role) VALUES (%s,%s,'admin')",
            (fake.unique.email(), fake.company()))
for _ in range(50):
    cur.execute(
        "INSERT INTO users (email, company, role) VALUES (%s,%s,'importer')",
        (fake.unique.email(), fake.company())
    )

# 2) Countries (static list)
countries = [
    ('United States','US'),
    ('China','CN'),
    ('Germany','DE'),
    ('Brazil','BR'),
    ('Japan','JP'),
]
for name, iso in countries:
    cur.execute("INSERT INTO countries (name, iso_code) VALUES (%s,%s)", (name,iso))

# fetch country IDs
cur.execute("SELECT id FROM countries")
country_ids = [r[0] for r in cur.fetchall()]

# 3) Product Categories
categories = ['Electronics','Textiles','Figurines','Foodstuffs','Machinery']
for cat in categories:
    cur.execute("INSERT INTO product_categories (name) VALUES (%s)", (cat,))

cur.execute("SELECT id,name FROM product_categories")
category_rows = cur.fetchall()
category_ids = [r[0] for r in category_rows]

# 4) Products: 100 random products
for _ in range(100):
    name = f"{fake.word().title()} {random.choice(['Pro','Max','Lite','X','Plus'])}"
    hs_code = f"{random.randint(100000,999999)}"
    cid = random.choice(category_ids)
    coid = random.choice(country_ids)
    cur.execute(
        "INSERT INTO products (name, hs_code, category_id, country_id) VALUES (%s,%s,%s,%s)",
        (name, hs_code, cid, coid)
    )

# 5) Tariff Rates: one per (country,category) with random effective dates
for coid in country_ids:
    for cid in category_ids:
        # 3 historical rates
        for months_ago in [12, 6, 1]:
            rate = round(random.uniform(1,15),2)
            eff = fake.date_between(start_date=f"-{months_ago}m", end_date="today")
            cur.execute(
                "INSERT INTO tariff_rates (country_id, category_id, rate_value, effective_from) VALUES (%s,%s,%s,%s)",
                (coid, cid, rate, eff)
            )

# 6) Import Declarations: 200 random
cur.execute("SELECT id FROM users WHERE role='importer'")
importer_ids = [r[0] for r in cur.fetchall()]
cur.execute("SELECT id, category_id FROM products")
prod_rows = cur.fetchall()

for _ in range(200):
    uid = random.choice(importer_ids)
    pid, prod_cat = random.choice(prod_rows)
    qty = random.randint(1,500)
    cost = round(random.uniform(5,500),2)
    status = random.choices(['draft','submitted','paid'], weights=[0.2,0.4,0.4])[0]
    decl_date = fake.date_between(start_date='-6m', end_date='today')
    cur.execute(
        "INSERT INTO import_declarations (user_id, product_id, quantity, unit_cost, status, declaration_date) "
        "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
        (uid, pid, qty, cost, status, decl_date)
    )
    decl_id = cur.fetchone()[0]

    # 7) Payments: only for submitted/paid declarations
    if status in ('submitted','paid'):
        # lookup the correct tariff
        cur.execute(
            "SELECT rate_value FROM tariff_rates "
            "WHERE country_id = (SELECT country_id FROM products WHERE id=%s) "
            "  AND category_id = %s "
            "  AND effective_from <= %s "
            "ORDER BY effective_from DESC LIMIT 1",
            (pid, prod_cat, decl_date)
        )
        raw_rate = cur.fetchone()[0]  # this is a Decimal
        rate = float(raw_rate) / 100.0
        amount = round(qty * cost * rate, 2)
        pay_status = 'pending' if status == 'submitted' else 'completed'
        paid_at = (fake.date_time_between_dates(
                     datetime_start=decl_date, datetime_end=fake.date_time_this_month())
                   if pay_status=='completed' else None)
        cur.execute(
            "INSERT INTO payments (declaration_id, amount, status, paid_at) VALUES (%s,%s,%s,%s)",
            (decl_id, amount, pay_status, paid_at)
        )

# commit all
conn.commit()
cur.close()
conn.close()
print("Seed complete!")