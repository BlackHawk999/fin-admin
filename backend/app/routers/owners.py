from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Owner
from ..schemas.owner import OwnerCreate, OwnerUpdate, OwnerResponse
from ..auth import get_current_user

router = APIRouter(prefix="/owners", tags=["owners"])


@router.get("", response_model=list[OwnerResponse])
def list_owners(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return db.query(Owner).all()


@router.post("", response_model=OwnerResponse, status_code=201)
def create_owner(
    data: OwnerCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    o = Owner(name=data.name, color_hex=data.color_hex)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


@router.get("/{owner_id}", response_model=OwnerResponse)
def get_owner(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    o = db.query(Owner).filter(Owner.id == owner_id).first()
    if not o:
        raise HTTPException(404, "Owner not found")
    return o


@router.patch("/{owner_id}", response_model=OwnerResponse)
def update_owner(
    owner_id: int,
    data: OwnerUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    o = db.query(Owner).filter(Owner.id == owner_id).first()
    if not o:
        raise HTTPException(404, "Owner not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(o, k, v)
    db.commit()
    db.refresh(o)
    return o


@router.delete("/{owner_id}", status_code=204)
def delete_owner(
    owner_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    o = db.query(Owner).filter(Owner.id == owner_id).first()
    if not o:
        raise HTTPException(404, "Owner not found")
    db.delete(o)
    db.commit()
