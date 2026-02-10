from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class PayerType(str, enum.Enum):
    owner = "owner"
    other = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount_uzs = Column(Numeric(15, 0), nullable=False)
    category = Column(String(255), nullable=False)
    comment = Column(String(500), nullable=True)
    payer_type = Column(SQLEnum(PayerType), nullable=False, default=PayerType.other)
    owner_id = Column(Integer, ForeignKey("owners.id", ondelete="SET NULL"), nullable=True)

    owner = relationship("Owner", backref="expenses")
