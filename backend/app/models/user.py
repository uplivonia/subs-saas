from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    # NEW FOR STRIPE CONNECT
    stripe_account_id = Column(String, nullable=True)
    stripe_onboarded = Column(Boolean, default=False)
