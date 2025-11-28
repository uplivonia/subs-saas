from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="payout_requests")

    # сколько вывести, в центах
    amount_cents = Column(BigInteger, nullable=False)

    # pending / approved / paid / rejected
    status = Column(String, default="pending", nullable=False)

    # snapshot реквизитов на момент заявки
    payout_method = Column(String, nullable=True)
    payout_details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
