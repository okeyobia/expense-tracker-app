# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run from the `frontend/` directory:

```bash
npm run dev      # Start dev server at http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

There is no test suite configured.

## Architecture

React + Vite app. No routing, no external state management. Frontend lives in `frontend/`, backend in `backend/`.

**Component tree:**

- `App` — holds the `transactions` array in state and `handleAdd`. Composes the three children below.
  - `Summary` — receives `transactions`, computes `totalIncome`, `totalExpenses`, and `balance` internally.
  - `TransactionForm` — owns its own form state; calls `onAdd(transaction)` prop on submit.
  - `TransactionList` — receives `transactions`, owns filter state (`filterType`, `filterCategory`) internally.

All styling is in `frontend/src/App.css`. Categories are a shared fixed list defined locally in `TransactionForm` and `TransactionList`.

**Data shape:**

```js
{ id, description, amount: number, type: "income"|"expense", category, date: "YYYY-MM-DD" }
```

Categories: `food`, `housing`, `utilities`, `transport`, `entertainment`, `salary`, `other`.

**Known intentional issues (part of the course):**

- No delete/edit functionality
- UI is deliberately plain
