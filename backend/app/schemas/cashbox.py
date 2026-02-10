from datetime import date
from pydantic import BaseModel, Field


class CashboxResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DailyCashboxEntryCreate(BaseModel):
    cashbox_id: int
    date: date
    amount_uzs: int
    comment: str | None = None


class DailyCashboxEntryResponse(BaseModel):
    id: int
    cashbox_id: int
    date: date
    amount_uzs: int
    comment: str | None = None

    class Config:
        from_attributes = True


class CashboxEntryUpdate(BaseModel):
    date: date
    amount_uzs: int
    comment: str | None = None
    edit_reason: str = Field(min_length=1, max_length=255)
