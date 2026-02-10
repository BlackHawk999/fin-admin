from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Cashbox(Base):
    __tablename__ = "cashboxes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    entries = relationship("DailyCashboxEntry", back_populates="cashbox", cascade="all, delete-orphan")


class DailyCashboxEntry(Base):
    __tablename__ = "daily_cashbox_entries"

    id = Column(Integer, primary_key=True, index=True)
    cashbox_id = Column(Integer, ForeignKey("cashboxes.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    amount_uzs = Column(Numeric(15, 0), nullable=False)
    comment = Column(String(500), nullable=True)

    cashbox = relationship("Cashbox", back_populates="entries")
