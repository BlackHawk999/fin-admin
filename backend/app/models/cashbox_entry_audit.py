from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text, Date
from sqlalchemy.orm import relationship
from ..database import Base


class CashboxEntryAudit(Base):
    __tablename__ = "cashbox_entry_audits"

    id = Column(Integer, primary_key=True, index=True)

    entry_id = Column(Integer, ForeignKey("daily_cashbox_entries.id", ondelete="CASCADE"), nullable=False)
    edited_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    edited_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    edit_reason = Column(String(255), nullable=False)

    old_date = Column(Date, nullable=True)
    old_amount_uzs = Column(Integer, nullable=True)
    old_comment = Column(Text, nullable=True)

    new_date = Column(Date, nullable=True)
    new_amount_uzs = Column(Integer, nullable=True)
    new_comment = Column(Text, nullable=True)

    entry = relationship("DailyCashboxEntry", backref="audits")
    user = relationship("User")
