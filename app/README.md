# App Directory

This `app/` directory contains the **deployed** backend API and frontend demo for the **TradeTariffManager** MVP, now running on a remote server. You no longer need to self‑host locally—just point your browser at the server IP.

---

## 1. Deployment URL

- **Frontend UI & Static Assets:**  
  http://38.180.205.35:3000

- **Backend API & Docs (FastAPI):**  
  http://38.180.205.35:8000/docs

---

## 2. Endpoints

### Users

- `GET /users`  
  List all importer users: returns `[ { id, email, company } ]`.

- `POST /users`  
  Create a new importer user.  
  **Body:** `{ "email": string, "company": string }`  
  **Returns:** `{ id, email, company }`.

### Products

- `GET /products`  
  List all products: returns `[ { id, name, hs_code } ]`.

- `POST /products`  
  Create a new product.  
  **Body:** `{ "name": string, "hs_code": string, "category_id": int, "country_id": int }`  
  **Returns:** `{ id, name, hs_code }`.

### Categories & Countries

- `GET /categories`  
  List all product categories: `[ { id, name } ]`.

- `GET /countries`  
  List all origin countries: `[ { id, name, iso_code } ]`.

### Import Declarations

- `GET /declarations`  
  List all import declarations with duties due.

- `POST /declarations`  
  Create a new import declaration.  
  **Body:** `{ "product_id": int, "user_id": int, "quantity": int, "unit_cost": float, "declaration_date": "YYYY-MM-DD" }`  
  **Returns:** the saved declaration with calculated `due`.

- `POST /declarations/{decl_id}/pay`  
  Pay duties for a submitted declaration.  
  **Path Param:** `decl_id`  
  **Returns:** `{ payment_id, declaration_id, amount, status }`.

---

## 3. How It Works (UI)

1. **Open** your browser to `http://38.180.205.35/`.
2. In the **Create New User** form, enter an email & company to add an importer.
3. In the **Create New Product** form, pick a category & country from dropdowns, enter name & HS code, then submit.
4. In the **Create Declaration** form, select a product & user, enter quantity, cost, and date, then submit.  Duties are calculated automatically.
5. Click **Pay** next to any `submitted` declaration to record a completed payment.
6. All results and table updates happen in‑page—no manual refresh required.

---

## 4. Architecture Notes

- **Backend:** FastAPI application serving JSON endpoints and static frontend files.
- **Frontend:** Plain HTML/JavaScript (no build step) mounted via FastAPI's `StaticFiles`.
- **Database:** PostgreSQL on `mydb` (hosted remotely) with schema and seed data.
- **CORS:** Configured to allow the remote frontend to call the API.

---

_No local setup is required—just point your browser at the server IP!_

