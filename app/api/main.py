import os
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg import connect
from psycopg.rows import dict_row
from typing import List
from datetime import date

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return connect(
        host="localhost",
        port=5432,
        dbname="mydb",
        user="postgres",
        password="1",
        row_factory=dict_row
    )

@app.get("/")
def health():
    return {"status": "OK"}

# --- Models ---
class Product(BaseModel):
    id: int
    name: str
    hs_code: str

class User(BaseModel):
    id: int
    email: str
    company: str

class DeclarationIn(BaseModel):
    product_id: int
    user_id: int
    quantity: int
    unit_cost: float
    declaration_date: str  # YYYY-MM-DD

class DeclarationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    unit_cost: float
    declaration_date: date
    status: str
    due: float

class PaymentOut(BaseModel):
    payment_id: int
    declaration_id: int
    amount: float
    status: str

# --- Endpoints ---
@app.get("/products", response_model=List[Product])
def list_products():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, hs_code FROM products ORDER BY id")
        return cur.fetchall()

@app.get("/users", response_model=List[User])
def list_users():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, email, company FROM users WHERE role='importer' ORDER BY id")
        return cur.fetchall()

@app.post("/declarations", response_model=DeclarationOut)
def create_declaration(data: DeclarationIn):
    with get_conn() as conn, conn.cursor() as cur:
        # fetch latest rate
        cur.execute("""
            SELECT tr.rate_value
            FROM tariff_rates tr
            JOIN products p
              ON p.country_id  = tr.country_id
             AND p.category_id = tr.category_id
            WHERE p.id = %s
              AND tr.effective_from <= %s
            ORDER BY tr.effective_from DESC
            LIMIT 1
        """, (data.product_id, data.declaration_date))
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "No tariff rate found")

        rate = float(row["rate_value"]) / 100.0

        # insert declaration
        cur.execute("""
            INSERT INTO import_declarations
              (user_id, product_id, quantity, unit_cost, status, declaration_date)
            VALUES (%s,%s,%s,%s,'submitted',%s)
            RETURNING id
        """, (
            data.user_id,
            data.product_id,
            data.quantity,
            data.unit_cost,
            data.declaration_date
        ))
        decl_id = cur.fetchone()["id"]
        conn.commit()

    due = round(data.quantity * data.unit_cost * rate, 2)
    return {
        "id": decl_id,
        "user_id": data.user_id,
        "product_id": data.product_id,
        "quantity": data.quantity,
        "unit_cost": data.unit_cost,
        "declaration_date": data.declaration_date,
        "status": "submitted",
        "due": due
    }

@app.get("/declarations", response_model=List[DeclarationOut])
def list_declarations():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT
              d.id,
              d.user_id,
              d.product_id,
              d.quantity,
              d.unit_cost,
              d.declaration_date,
              d.status,
              -- cast to numeric before rounding:
              ROUND(
                (
                  d.quantity::numeric
                  * d.unit_cost::numeric
                  * (lr.rate_value / 100.0)
                )::numeric
              , 2
              ) AS due
            FROM import_declarations d
            JOIN LATERAL (
              SELECT tr.rate_value
              FROM tariff_rates tr
              JOIN products p
                ON p.country_id  = tr.country_id
               AND p.category_id = tr.category_id
              WHERE p.id = d.product_id
                AND tr.effective_from <= d.declaration_date
              ORDER BY tr.effective_from DESC
              LIMIT 1
            ) AS lr ON TRUE
            ORDER BY d.declaration_date DESC, d.id DESC;
        """)
        return cur.fetchall()

@app.post("/declarations/{decl_id}/pay", response_model=PaymentOut)
def pay_declaration(decl_id: int = Path(..., title="Declaration ID")):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT status, quantity, unit_cost FROM import_declarations WHERE id=%s",
            (decl_id,)
        )
        rec = cur.fetchone()
        if not rec:
            raise HTTPException(404, "Declaration not found")
        if rec["status"] != "submitted":
            raise HTTPException(400, "Already paid or invalid status")

        # fetch rate again
        cur.execute("""
            SELECT tr.rate_value
            FROM tariff_rates tr
            JOIN products p
              ON p.country_id  = tr.country_id
             AND p.category_id = tr.category_id
            WHERE p.id = %s
              AND tr.effective_from <= (
                SELECT declaration_date
                FROM import_declarations WHERE id=%s
              )
            ORDER BY tr.effective_from DESC
            LIMIT 1
        """, (decl_id, decl_id))
        rr = cur.fetchone()

        qty   = float(rec["quantity"])
        cost  = float(rec["unit_cost"])
        rate  = float(rr["rate_value"]) / 100.0 if rr else 0.0
        amount = round(qty * cost * rate, 2)

        cur.execute("""
            INSERT INTO payments (declaration_id, amount, status, paid_at)
            VALUES (%s,%s,'completed',NOW()) RETURNING id
        """, (decl_id, amount))
        pay_id = cur.fetchone()["id"]

        cur.execute(
            "UPDATE import_declarations SET status='paid' WHERE id=%s",
            (decl_id,)
        )
        conn.commit()

    return {"payment_id": pay_id, "declaration_id": decl_id, "amount": amount, "status": "completed"}
