from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Cashbox, DailyCashboxEntry
from ..schemas.cashbox import (
    CashboxResponse,
    CashboxCreate,
    DailyCashboxEntryCreate,
    DailyCashboxEntryResponse,
    CashboxEntryUpdate,
)
from ..auth import get_current_user
from ..models.cashbox_entry_audit import CashboxEntryAudit

router = APIRouter(prefix="/cashboxes", tags=["cashboxes"])

MAX_CASHBOXES = 5


def _entry_to_response(e: DailyCashboxEntry) -> DailyCashboxEntryResponse:
    cash_in = int(e.cash_in_uzs)
    card_in = int(e.card_in_uzs)
    click_in = int(e.click_payme_in_uzs)
    bonus = int(e.bonus_spent_uzs)
    exp_company = int(e.cash_exp_company_uzs)
    exp_other = int(e.cash_exp_other_uzs)

    total_income = cash_in + card_in + click_in
    exp_total = exp_company + exp_other

    return DailyCashboxEntryResponse(
        id=e.id,
        cashbox_id=e.cashbox_id,
        date=e.date,
        cash_in_uzs=cash_in,
        card_in_uzs=card_in,
        click_payme_in_uzs=click_in,
        bonus_spent_uzs=bonus,
        cash_exp_company_uzs=exp_company,
        cash_exp_other_uzs=exp_other,
        comment=e.comment,
        total_income_uzs=total_income,
        net_sales_uzs=total_income - bonus,
        cash_exp_total_uzs=exp_total,
        cash_end_uzs=cash_in - exp_total,
    )


@router.get("", response_model=list[CashboxResponse])
def list_cashboxes(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return db.query(Cashbox).order_by(Cashbox.id).all()


@router.post("", response_model=CashboxResponse, status_code=201)
def create_cashbox(
    payload: CashboxCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    total = db.query(func.count(Cashbox.id)).scalar() or 0
    if total >= MAX_CASHBOXES:
        raise HTTPException(status_code=400, detail=f"Max {MAX_CASHBOXES} cashboxes allowed")

    exists = db.query(Cashbox).filter(func.lower(Cashbox.name) == name.lower()).first()
    if exists:
        raise HTTPException(status_code=400, detail="Cashbox with this name already exists")

    cb = Cashbox(name=name)
    db.add(cb)
    db.commit()
    db.refresh(cb)
    return cb


@router.get("/{cashbox_id}", response_model=CashboxResponse)
def get_cashbox(
    cashbox_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(Cashbox).filter(Cashbox.id == cashbox_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cashbox not found")
    return c


@router.get("/{cashbox_id}/entries", response_model=list[DailyCashboxEntryResponse])
def list_entries(
    cashbox_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 200,
):
    q = db.query(DailyCashboxEntry).filter(DailyCashboxEntry.cashbox_id == cashbox_id)
    if date_from:
        q = q.filter(DailyCashboxEntry.date >= date_from)
    if date_to:
        q = q.filter(DailyCashboxEntry.date <= date_to)
    q = q.order_by(DailyCashboxEntry.date.desc())
    rows = q.offset(skip).limit(limit).all()
    return [_entry_to_response(e) for e in rows]


@router.get("/{cashbox_id}/entries/sum")
def entries_sum(
    cashbox_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
):
    row = (
        db.query(
            func.coalesce(func.sum(DailyCashboxEntry.cash_in_uzs), 0).label("cash_in"),
            func.coalesce(func.sum(DailyCashboxEntry.card_in_uzs), 0).label("card_in"),
            func.coalesce(func.sum(DailyCashboxEntry.click_payme_in_uzs), 0).label("click_in"),
            func.coalesce(func.sum(DailyCashboxEntry.bonus_spent_uzs), 0).label("bonus_spent"),
            func.coalesce(func.sum(DailyCashboxEntry.cash_exp_company_uzs), 0).label("exp_company"),
            func.coalesce(func.sum(DailyCashboxEntry.cash_exp_other_uzs), 0).label("exp_other"),
        )
        .filter(
            DailyCashboxEntry.cashbox_id == cashbox_id,
            DailyCashboxEntry.date >= date_from,
            DailyCashboxEntry.date <= date_to,
        )
        .one()
    )

    cash_in = int(row.cash_in)
    card_in = int(row.card_in)
    click_in = int(row.click_in)
    bonus = int(row.bonus_spent)
    exp_company = int(row.exp_company)
    exp_other = int(row.exp_other)

    total_income = cash_in + card_in + click_in
    exp_total = exp_company + exp_other

    return {
        "cash_in_uzs": cash_in,
        "card_in_uzs": card_in,
        "click_payme_in_uzs": click_in,
        "total_income_uzs": total_income,
        "bonus_spent_uzs": bonus,
        "net_sales_uzs": total_income - bonus,
        "cash_exp_company_uzs": exp_company,
        "cash_exp_other_uzs": exp_other,
        "cash_exp_total_uzs": exp_total,
        "cash_end_uzs": cash_in - exp_total,
    }


@router.post("/entries", response_model=DailyCashboxEntryResponse, status_code=201)
def create_entry(
    data: DailyCashboxEntryCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(Cashbox).filter(Cashbox.id == data.cashbox_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cashbox not found")

    e = DailyCashboxEntry(
        cashbox_id=data.cashbox_id,
        date=data.date,
        cash_in_uzs=data.cash_in_uzs,
        card_in_uzs=data.card_in_uzs,
        click_payme_in_uzs=data.click_payme_in_uzs,
        bonus_spent_uzs=data.bonus_spent_uzs,
        cash_exp_company_uzs=data.cash_exp_company_uzs,
        cash_exp_other_uzs=data.cash_exp_other_uzs,
        comment=data.comment,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return _entry_to_response(e)


@router.patch("/entries/{entry_id}", response_model=DailyCashboxEntryResponse)
def update_entry(
    entry_id: int,
    payload: CashboxEntryUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    entry = db.query(DailyCashboxEntry).filter(DailyCashboxEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if not payload.edit_reason.strip():
        raise HTTPException(status_code=400, detail="Edit reason is required")

    # old values
    old_date = entry.date
    old_cash_in = int(entry.cash_in_uzs)
    old_card_in = int(entry.card_in_uzs)
    old_click_in = int(entry.click_payme_in_uzs)
    old_bonus = int(entry.bonus_spent_uzs)
    old_exp_company = int(entry.cash_exp_company_uzs)
    old_exp_other = int(entry.cash_exp_other_uzs)
    old_comment = entry.comment

    # apply new
    entry.date = payload.date
    entry.cash_in_uzs = payload.cash_in_uzs
    entry.card_in_uzs = payload.card_in_uzs
    entry.click_payme_in_uzs = payload.click_payme_in_uzs
    entry.bonus_spent_uzs = payload.bonus_spent_uzs
    entry.cash_exp_company_uzs = payload.cash_exp_company_uzs
    entry.cash_exp_other_uzs = payload.cash_exp_other_uzs
    entry.comment = payload.comment

    # audit log
    audit = CashboxEntryAudit(
        entry_id=entry.id,
        edited_by_user_id=user.id,
        edit_reason=payload.edit_reason.strip(),

        old_date=old_date,
        old_cash_in_uzs=old_cash_in,
        old_card_in_uzs=old_card_in,
        old_click_payme_in_uzs=old_click_in,
        old_bonus_spent_uzs=old_bonus,
        old_cash_exp_company_uzs=old_exp_company,
        old_cash_exp_other_uzs=old_exp_other,
        old_comment=old_comment,

        new_date=payload.date,
        new_cash_in_uzs=int(payload.cash_in_uzs),
        new_card_in_uzs=int(payload.card_in_uzs),
        new_click_payme_in_uzs=int(payload.click_payme_in_uzs),
        new_bonus_spent_uzs=int(payload.bonus_spent_uzs),
        new_cash_exp_company_uzs=int(payload.cash_exp_company_uzs),
        new_cash_exp_other_uzs=int(payload.cash_exp_other_uzs),
        new_comment=payload.comment,
    )
    db.add(audit)

    db.commit()
    db.refresh(entry)
    return _entry_to_response(entry)