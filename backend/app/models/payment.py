from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, ForeignKey
from sqlalchemy.sql import func

from app.db.base_class import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, index=True, nullable=False)

    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    stripe_session_id = Column(String(255), unique=True, index=True, nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)

    status = Column(String(20), nullable=False, default="pending")
    # pending, paid, failed, canceled

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )