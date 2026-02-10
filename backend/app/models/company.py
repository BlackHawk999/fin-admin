from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class TransactionDirection(str, enum.Enum):
    OUT = "OUT"  # дали деньги
    IN = "IN"    # получили


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    transactions = relationship("CompanyTransaction", back_populates="company", cascade="all, delete-orphan")


class CompanyTransaction(Base):
    __tablename__ = "company_transactions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    amount_uzs = Column(Numeric(15, 0), nullable=False)
    direction = Column(SQLEnum(TransactionDirection), nullable=False)
    comment = Column(String(500), nullable=True)

    company = relationship("Company", back_populates="transactions")
