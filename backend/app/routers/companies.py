from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Company, CompanyTransaction
from ..models.company import TransactionDirection
from ..schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyTransactionCreate,
    CompanyTransactionResponse,
)
from ..auth import get_current_user

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: str | None = None,
    is_active: bool | None = None,
):
    q = db.query(Company)
    if search:
        q = q.filter(Company.name.ilike(f"%{search}%"))
    if is_active is not None:
        q = q.filter(Company.is_active == is_active)
    return q.all()


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(
    data: CompanyCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = Company(name=data.name, is_active=data.is_active)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    return c


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    db.delete(c)
    db.commit()


# Transactions
@router.get("/{company_id}/transactions", response_model=list[CompanyTransactionResponse])
def list_transactions(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 200,
):
    q = db.query(CompanyTransaction).filter(CompanyTransaction.company_id == company_id)
    if date_from:
        q = q.filter(CompanyTransaction.date >= date_from)
    if date_to:
        q = q.filter(CompanyTransaction.date <= date_to)
    q = q.order_by(CompanyTransaction.date.desc())
    return q.offset(skip).limit(limit).all()


@router.get("/{company_id}/transactions/balance")
def transactions_balance(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
):
    q = db.query(CompanyTransaction).filter(
        CompanyTransaction.company_id == company_id,
        CompanyTransaction.date >= date_from,
        CompanyTransaction.date <= date_to,
    )
    total = 0
    for t in q.all():
        if t.direction == TransactionDirection.IN:
            total += int(t.amount_uzs)
        else:
            total -= int(t.amount_uzs)
    return {"balance_uzs": total}


@router.post("/{company_id}/transactions", response_model=CompanyTransactionResponse, status_code=201)
def create_transaction(
    company_id: int,
    data: CompanyTransactionCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    t = CompanyTransaction(
        company_id=company_id,
        date=data.date,
        amount_uzs=data.amount_uzs,
        direction=data.direction,
        comment=data.comment,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{company_id}/transactions/{transaction_id}", status_code=204)
def delete_transaction(
    company_id: int,
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    t = (
        db.query(CompanyTransaction)
        .filter(
            CompanyTransaction.id == transaction_id,
            CompanyTransaction.company_id == company_id,
        )
        .first()
    )
    if not t:
        raise HTTPException(404, "Transaction not found")
    db.delete(t)
    db.commit()
