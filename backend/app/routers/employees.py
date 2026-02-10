from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Employee, Advance
from ..schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, AdvanceCreate, AdvanceResponse
from ..auth import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 100,
):
    q = db.query(Employee)
    if search:
        q = q.filter(Employee.full_name.ilike(f"%{search}%"))
    if is_active is not None:
        q = q.filter(Employee.is_active == is_active)
    return q.offset(skip).limit(limit).all()


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(
    data: EmployeeCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    emp = Employee(
        full_name=data.full_name,
        monthly_salary_uzs=data.monthly_salary_uzs,
        is_active=data.is_active,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    db.delete(emp)
    db.commit()


# Advances
@router.get("/{employee_id}/advances", response_model=list[AdvanceResponse])
def list_advances(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 200,
):
    q = db.query(Advance).filter(Advance.employee_id == employee_id)
    if date_from:
        q = q.filter(Advance.date >= date_from)
    if date_to:
        q = q.filter(Advance.date <= date_to)
    q = q.order_by(Advance.date.desc())
    return q.offset(skip).limit(limit).all()


@router.get("/{employee_id}/advances/sum")
def advances_sum(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    date_from: date,
    date_to: date,
):
    r = (
        db.query(func.coalesce(func.sum(Advance.amount_uzs), 0))
        .filter(
            Advance.employee_id == employee_id,
            Advance.date >= date_from,
            Advance.date <= date_to,
        )
        .scalar()
    )
    return {"sum_uzs": int(r)}


@router.post("/{employee_id}/advances", response_model=AdvanceResponse, status_code=201)
def create_advance(
    employee_id: int,
    data: AdvanceCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    adv = Advance(
        employee_id=employee_id,
        date=data.date,
        amount_uzs=data.amount_uzs,
        comment=data.comment,
    )
    db.add(adv)
    db.commit()
    db.refresh(adv)
    return adv


@router.delete("/{employee_id}/advances/{advance_id}", status_code=204)
def delete_advance(
    employee_id: int,
    advance_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    adv = (
        db.query(Advance)
        .filter(Advance.id == advance_id, Advance.employee_id == employee_id)
        .first()
    )
    if not adv:
        raise HTTPException(404, "Advance not found")
    db.delete(adv)
    db.commit()
