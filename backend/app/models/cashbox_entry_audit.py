# backend/app/models/cashbox_entry_audit.py
from datetime import datetime, date as date_type

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from ..database import Base


class CashboxEntryAudit(Base):
    __tablename__ = "cashbox_entry_audits"

    id = Column(Integer, primary_key=True, index=True)

    entry_id = Column(Integer, ForeignKey("daily_cashbox_entries.id", ondelete="CASCADE"), nullable=False)
    edited_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    edit_reason = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # old values
    old_date = Column(Date, nullable=False)
    old_amount_uzs = Column(Numeric(15, 0), nullable=False)
    old_comment = Column(String(500), nullable=True)

    # new values
    new_date = Column(Date, nullable=False)
    new_amount_uzs = Column(Numeric(15, 0), nullable=False)
    new_comment = Column(String(500), nullable=True)

    # relationships (optional, but nice)
    entry = relationship("DailyCashboxEntry", lazy="joined")
    edited_by = relationship("User", lazy="joined")
