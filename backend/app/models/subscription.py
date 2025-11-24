from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean

from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    end_user_id = Column(Integer, ForeignKey("end_users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_at = Column(DateTime, default=datetime.utcnow)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, default="active")  # active / expired / canceled
    auto_renew = Column(Boolean, default=False)
