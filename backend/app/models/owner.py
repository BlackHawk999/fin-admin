from sqlalchemy import Column, Integer, String
from ..database import Base


class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    color_hex = Column(String(7), nullable=False, default="#808080")
