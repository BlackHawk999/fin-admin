from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..models.expense_category import ExpenseCategory
from ..schemas.expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
)

router = APIRouter(prefix="/expense-categories", tags=["expense-categories"])


@router.get("", response_model=list[ExpenseCategoryResponse])
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    active_only: bool = True,
):
    q = db.query(ExpenseCategory)
    if active_only:
        q = q.filter(ExpenseCategory.is_active == True)  # noqa: E712
    return q.order_by(ExpenseCategory.name.asc()).all()


@router.post("", response_model=ExpenseCategoryResponse, status_code=201)
def create_category(
    data: ExpenseCategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "Category name is required")

    exists = db.query(ExpenseCategory).filter(ExpenseCategory.name == name).first()
    if exists:
        raise HTTPException(400, "Category already exists")

    c = ExpenseCategory(name=name, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/{category_id}", response_model=ExpenseCategoryResponse)
def update_category(
    category_id: int,
    data: ExpenseCategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    c = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
    if not c:
        raise HTTPException(404, "Category not found")

    payload = data.model_dump(exclude_unset=True)

    if "name" in payload and payload["name"] is not None:
        new_name = payload["name"].strip()
        if not new_name:
            raise HTTPException(400, "Category name is required")
        dup = db.query(ExpenseCategory).filter(ExpenseCategory.name == new_name, ExpenseCategory.id != c.id).first()
        if dup:
            raise HTTPException(400, "Category already exists")
        c.name = new_name

    if "is_active" in payload and payload["is_active"] is not None:
        c.is_active = payload["is_active"]

    db.commit()
    db.refresh(c)
    return c
