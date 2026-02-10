from datetime import date
from pydantic import BaseModel
from app.models.company import TransactionDirection


class CompanyCreate(BaseModel):
    name: str
    is_active: bool = True


class CompanyUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class CompanyTransactionCreate(BaseModel):
    date: date
    amount_uzs: int
    direction: TransactionDirection
    comment: str | None = None


class CompanyTransactionResponse(BaseModel):
    id: int
    company_id: int
    date: date
    amount_uzs: int
    direction: TransactionDirection
    comment: str | None = None

    class Config:
        from_attributes = True
