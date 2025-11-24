from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric

from app.db.base_class import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="EUR")
    duration_days = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
