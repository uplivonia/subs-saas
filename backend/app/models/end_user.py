from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime

from app.db.base_class import Base


class EndUser(Base):
    __tablename__ = "end_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
