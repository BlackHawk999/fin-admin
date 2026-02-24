from datetime import date
from pydantic import BaseModel, Field


class CashboxCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CashboxResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DailyCashboxEntryCreate(BaseModel):
    cashbox_id: int
    date: date

    # incomes
    cash_in_uzs: int = Field(default=0, ge=0)
    card_in_uzs: int = Field(default=0, ge=0)
    click_payme_in_uzs: int = Field(default=0, ge=0)

    # bonuses
    bonus_spent_uzs: int = Field(default=0, ge=0)

    # expenses (cash only)
    cash_exp_company_uzs: int = Field(default=0, ge=0)
    cash_exp_other_uzs: int = Field(default=0, ge=0)

    comment: str | None = None


class DailyCashboxEntryResponse(BaseModel):
    id: int
    cashbox_id: int
    date: date

    cash_in_uzs: int
    card_in_uzs: int
    click_payme_in_uzs: int

    bonus_spent_uzs: int

    cash_exp_company_uzs: int
    cash_exp_other_uzs: int

    comment: str | None = None

    # computed (удобно фронту)
    total_income_uzs: int
    net_sales_uzs: int
    cash_exp_total_uzs: int
    cash_end_uzs: int

    class Config:
        from_attributes = True


class CashboxEntryUpdate(BaseModel):
    date: date

    cash_in_uzs: int = Field(default=0, ge=0)
    card_in_uzs: int = Field(default=0, ge=0)
    click_payme_in_uzs: int = Field(default=0, ge=0)

    bonus_spent_uzs: int = Field(default=0, ge=0)

    cash_exp_company_uzs: int = Field(default=0, ge=0)
    cash_exp_other_uzs: int = Field(default=0, ge=0)

    comment: str | None = None
    edit_reason: str = Field(min_length=1, max_length=255)