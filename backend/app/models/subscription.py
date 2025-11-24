from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    end_user_id = Column(Integer, ForeignKey("end_users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)

    # 🔽 Добавляем это:
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    start_at = Column(DateTime, default=datetime.utcnow)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, default="active")  # active / expired / canceled
    auto_renew = Column(Boolean, default=False)
