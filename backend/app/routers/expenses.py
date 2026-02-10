from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Expense, Owner
from ..schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from ..auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


def expense_to_response(e: Expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=e.id,
        date=e.date,
        amount_uzs=int(e.amount_uzs),
        category=e.category,
        comment=e.comment,
        payer_type=e.payer_type,
        owner_id=e.owner_id,
    )


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
    category: str | None = None,
    owner_id: int | None = None,
    skip: int = 0,
    limit: int = 200,
):
    q = db.query(Expense)
    if date_from:
        q = q.filter(Expense.date >= date_from)
    if date_to:
        q = q.filter(Expense.date <= date_to)
    if category:
        q = q.filter(Expense.category.ilike(f"%{category}%"))
    if owner_id is not None:
        q = q.filter(Expense.owner_id == owner_id)
    q = q.order_by(Expense.date.desc())
    return [expense_to_response(e) for e in q.offset(skip).limit(limit).all()]


@router.get("/sum")
def expenses_sum(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
    category: str | None = None,
    owner_id: int | None = None,
):
    q = db.query(func.coalesce(func.sum(Expense.amount_uzs), 0)).filter(
        Expense.date >= date_from,
        Expense.date <= date_to,
    )
    if category:
        q = q.filter(Expense.category.ilike(f"%{category}%"))
    if owner_id is not None:
        q = q.filter(Expense.owner_id == owner_id)
    r = q.scalar()
    return {"sum_uzs": int(r)}


@router.get("/by-day")
def expenses_by_day(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
):
    """For charts: sum by date."""
    rows = (
        db.query(Expense.date, func.sum(Expense.amount_uzs).label("total"))
        .filter(Expense.date >= date_from, Expense.date <= date_to)
        .group_by(Expense.date)
        .order_by(Expense.date)
        .all()
    )
    return [{"date": str(d), "total_uzs": int(t)} for d, t in rows]


@router.get("/by-category")
def expenses_by_category(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
):
    """For charts: sum by category."""
    rows = (
        db.query(Expense.category, func.sum(Expense.amount_uzs).label("total"))
        .filter(Expense.date >= date_from, Expense.date <= date_to)
        .group_by(Expense.category)
        .all()
    )
    return [{"category": c, "total_uzs": int(t)} for c, t in rows]


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(
    data: ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    e = Expense(
        date=data.date,
        amount_uzs=data.amount_uzs,
        category=data.category,
        comment=data.comment,
        payer_type=data.payer_type,
        owner_id=data.owner_id,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return expense_to_response(e)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Expense not found")
    return expense_to_response(e)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Expense not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(e, k, v)
    db.commit()
    db.refresh(e)
    return expense_to_response(e)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Expense not found")
    db.delete(e)
    db.commit()
