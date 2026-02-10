from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    full_name: str
    monthly_salary_uzs: int = 0
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    full_name: str | None = None
    monthly_salary_uzs: int | None = None
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: int
    full_name: str
    monthly_salary_uzs: int
    is_active: bool

    class Config:
        from_attributes = True


class AdvanceCreate(BaseModel):
    date: date
    amount_uzs: int
    comment: str | None = None


class AdvanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    amount_uzs: int
    comment: str | None = None

    class Config:
        from_attributes = True
