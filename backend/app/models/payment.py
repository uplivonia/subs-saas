from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, DateTime

from app.db.base_class import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    provider = Column(String, nullable=False)  # stripe / paypal / ton
    provider_payment_id = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="EUR")
    status = Column(String, default="pending")  # pending / paid / failed
    created_at = Column(DateTime, default=datetime.utcnow)
