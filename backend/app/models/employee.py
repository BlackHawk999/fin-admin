from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    monthly_salary_uzs = Column(Numeric(15, 0), nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)

    advances = relationship("Advance", back_populates="employee", cascade="all, delete-orphan")


class Advance(Base):
    __tablename__ = "advances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    amount_uzs = Column(Numeric(15, 0), nullable=False)
    comment = Column(String(500), nullable=True)

    employee = relationship("Employee", back_populates="advances")
