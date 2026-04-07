# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start dev server at http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

There is no test suite configured.

## Architecture

This is a single-component React app (`src/App.jsx`) using Vite. All state and logic live in one `App` component — no routing, no external state management, no backend.

**Known intentional issues (part of the course):**

- Bug: `amount` is stored as a string, so `reduce` concatenates instead of summing — totals are wrong
- Transaction 4 ("Freelance Work") is marked `type: "income"` in the seed data but `category: "salary"` with `type: "expense"` — inconsistent seed data
- UI is deliberately plain; styling is in `src/App.css`
- No delete/edit functionality

**Data shape:**

```js
{ id, description, amount, type: "income"|"expense", category, date: "YYYY-MM-DD" }
```

Categories are a fixed list: `food`, `housing`, `utilities`, `transport`, `entertainment`, `salary`, `other`.
