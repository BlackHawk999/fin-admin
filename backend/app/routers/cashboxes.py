from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Cashbox, DailyCashboxEntry
from ..schemas.cashbox import (
    CashboxResponse,
    DailyCashboxEntryCreate,
    DailyCashboxEntryResponse,
    CashboxEntryUpdate,
)
from ..auth import get_current_user
from ..models.cashbox_entry_audit import CashboxEntryAudit

router = APIRouter(prefix="/cashboxes", tags=["cashboxes"])


@router.get("", response_model=list[CashboxResponse])
def list_cashboxes(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return db.query(Cashbox).order_by(Cashbox.id).all()


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
    return q.offset(skip).limit(limit).all()


@router.get("/{cashbox_id}/entries/sum")
def entries_sum(
    cashbox_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
):
    r = (
        db.query(func.coalesce(func.sum(DailyCashboxEntry.amount_uzs), 0))
        .filter(
            DailyCashboxEntry.cashbox_id == cashbox_id,
            DailyCashboxEntry.date >= date_from,
            DailyCashboxEntry.date <= date_to,
        )
        .scalar()
    )
    return {"sum_uzs": int(r)}


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
        amount_uzs=data.amount_uzs,
        comment=data.comment,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


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
    old_amount = int(entry.amount_uzs)
    old_comment = entry.comment

    # apply new
    entry.date = payload.date
    entry.amount_uzs = payload.amount_uzs
    entry.comment = payload.comment

    # audit log
    audit = CashboxEntryAudit(
        entry_id=entry.id,
        edited_by_user_id=user.id,
        edit_reason=payload.edit_reason.strip(),
        old_date=old_date,
        old_amount_uzs=old_amount,
        old_comment=old_comment,
        new_date=payload.date,
        new_amount_uzs=int(payload.amount_uzs),
        new_comment=payload.comment,
    )
    db.add(audit)

    db.commit()
    db.refresh(entry)
    return entry
