import datetime as dt

from pydantic import BaseModel
from app.models.expense import PayerType


class ExpenseCreate(BaseModel):
    date: dt.date
    amount_uzs: int
    category: str
    comment: str | None = None
    payer_type: PayerType = PayerType.other
    owner_id: int | None = None


class ExpenseUpdate(BaseModel):
    date: dt.date | None = None
    amount_uzs: int | None = None
    category: str | None = None
    comment: str | None = None
    payer_type: PayerType | None = None
    owner_id: int | None = None


class ExpenseResponse(BaseModel):
    id: int
    date: dt.date
    amount_uzs: int
    category: str
    comment: str | None = None
    payer_type: PayerType
    owner_id: int | None = None

    class Config:
        from_attributes = True
