# App Directory

This `app/` directory contains the backend API and frontend demo for the TradeTariffManager MVP.

## Structure

```
app/
├── api/
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Python dependencies
└── frontend/
    └── index.html       # Simple HTML/JS form demo
```

---

## Prerequisites

- Python 3.9+ installed
- A running PostgreSQL database named `mydb` with schema and seed data loaded (see `../database/README.md`)
- The file `database/.env` populated with:

  ```dotenv
  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  POSTGRES_DB=mydb
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=YourPassword
  ```

---

## 1. Run the Backend

1. Open a terminal and navigate to the backend folder:

   ```bash
   cd app/api
   ```

2. (Optional) Activate your virtual environment:

   ```bash
   ../../../.venv/Scripts/Activate.ps1    # Windows PowerShell
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

5. The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

---

## 2. Run the Frontend Demo

1. Open a new terminal and navigate to the frontend folder:

   ```bash
   cd app/frontend
   ```

2. Serve the `index.html` file. For example, using Python's built‑in server:

   ```bash
   python -m http.server 3000
   ```

3. Open your browser to `http://localhost:3000`. You will see a form to:
   - Select an existing product ID and user ID
   - Enter quantity, unit cost, and date
   - Create a declaration and automatically process a payment

4. After submission, the form will display the API responses for both the declaration and payment.

---

## 3. How It Works

- The **backend** (`main.py`) exposes three endpoints:
  - `GET /tariff-rate?country_id=<>&category_id=<>` — lookup current duty rate
  - `POST /declarations` — create a new import declaration and return calculated duty
  - `POST /payments` — record a payment and mark the declaration as paid

- The **frontend** is a minimal HTML/JS form that sends requests to these endpoints.

---

