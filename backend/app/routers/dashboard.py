from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Expense, DailyCashboxEntry, CompanyTransaction
from ..models.company import TransactionDirection
from ..auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    today_d = date.today()
    first_day = today_d.replace(day=1)
    # expenses today
    exp_today = (
        db.query(func.coalesce(func.sum(Expense.amount_uzs), 0))
        .filter(Expense.date == today_d)
        .scalar()
    )
    # expenses this month
    exp_month = (
        db.query(func.coalesce(func.sum(Expense.amount_uzs), 0))
        .filter(Expense.date >= first_day, Expense.date <= today_d)
        .scalar()
    )
    # cashboxes today total (all entries for today)
    cash_today = (
        db.query(func.coalesce(func.sum(DailyCashboxEntry.amount_uzs), 0))
        .filter(DailyCashboxEntry.date == today_d)
        .scalar()
    )
    # companies OUT this month
    companies_out = (
        db.query(func.coalesce(func.sum(CompanyTransaction.amount_uzs), 0))
        .filter(
            CompanyTransaction.direction == TransactionDirection.OUT,
            CompanyTransaction.date >= first_day,
            CompanyTransaction.date <= today_d,
        )
        .scalar()
    )
    return {
        "expenses_today_uzs": int(exp_today),
        "expenses_this_month_uzs": int(exp_month),
        "cashboxes_today_total_uzs": int(cash_today),
        "companies_out_this_month_uzs": int(companies_out),
    }
