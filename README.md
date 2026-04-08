# Expense Tracker

A full-stack expense tracker with a React frontend and a FastAPI/PostgreSQL backend.

## Stack

### Frontend
- React + Vite
- No external state management or routing

### Backend
- FastAPI (Python)
- PostgreSQL via SQLModel + psycopg2
- JWT authentication (python-jose, argon2 password hashing)

## Features

- User registration and login (JWT-based auth, tokens persisted in localStorage)
- View income and expense transactions with a financial summary (balance, total income, total expenses)
- Add new transactions (description, amount, type, category, date)
- Delete transactions
- Filter transactions by type and category
- Protected API — all transaction endpoints require a valid token
- Seeded with sample data on first run

## Project Structure

```text
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Root component — holds transactions state, auth state
│   │   ├── AuthForm.jsx        # Login / register form
│   │   ├── Summary.jsx         # Balance, income, expenses totals
│   │   ├── TransactionForm.jsx
│   │   └── TransactionList.jsx
│   ├── index.html
│   └── vite.config.js
└── backend/
    ├── main.py                 # FastAPI app, routes, Transaction model
    ├── auth.py                 # User model, JWT helpers, password hashing
    └── database.py             # SQLModel engine, session dependency
```

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres@localhost/expense_tracker
JWT_SECRET=your-secret-key
```

```bash
uvicorn main:app --reload
```

The frontend proxies `/api` requests to `http://localhost:8000` (configured in `frontend/vite.config.js`).

## Frontend Scripts

```bash
npm run dev      # Start dev server at http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

> **Note:** When querying the users table directly in PostgreSQL, use `SELECT * FROM "user";` — `user` is a reserved keyword and requires double-quotes.
