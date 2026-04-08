from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, select

from database import create_db_and_tables, get_session
from auth import (
    User, UserCreate, Token,
    hash_password, verify_password, create_access_token,
    get_current_user,
)


# ── Model ─────────────────────────────────────────────────────────────────────

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    amount: float
    type: str        # "income" | "expense"
    category: str
    date: str        # YYYY-MM-DD


class TransactionCreate(SQLModel):
    description: str
    amount: float
    type: str
    category: str
    date: str


# ── Seed data ─────────────────────────────────────────────────────────────────

SEED = [
    {"description": "Salary",        "amount": 5000, "type": "income",  "category": "salary",        "date": "2025-01-01"},
    {"description": "Rent",          "amount": 1200, "type": "expense", "category": "housing",       "date": "2025-01-02"},
    {"description": "Groceries",     "amount": 150,  "type": "expense", "category": "food",          "date": "2025-01-03"},
    {"description": "Freelance Work","amount": 800,  "type": "income",  "category": "salary",        "date": "2025-01-05"},
    {"description": "Electric Bill", "amount": 95,   "type": "expense", "category": "utilities",     "date": "2025-01-06"},
    {"description": "Dinner Out",    "amount": 65,   "type": "expense", "category": "food",          "date": "2025-01-07"},
    {"description": "Gas",           "amount": 45,   "type": "expense", "category": "transport",     "date": "2025-01-08"},
    {"description": "Netflix",       "amount": 15,   "type": "expense", "category": "entertainment", "date": "2025-01-10"},
]


# ── App lifecycle ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    from database import engine
    with Session(engine) as session:
        if not session.exec(select(Transaction)).first():
            for row in SEED:
                session.add(Transaction(**row))
            session.commit()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────────────────

# ── Auth routes ────────────────────────────────────────────────────────────────

@app.post("/api/auth/register", response_model=Token, status_code=201)
def register(body: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    session.add(user)
    session.commit()
    return Token(access_token=create_access_token(user.email))


@app.post("/api/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.email))


# ── Transaction routes ─────────────────────────────────────────────────────────

@app.get("/api/transactions", response_model=list[Transaction])
def list_transactions(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    return session.exec(select(Transaction)).all()


@app.post("/api/transactions", response_model=Transaction, status_code=201)
def create_transaction(
    body: TransactionCreate,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    transaction = Transaction(**body.model_dump())
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@app.delete("/api/transactions/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
