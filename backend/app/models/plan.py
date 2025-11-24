from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey

from app.db.base_class import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"  # таблица тарифов

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="EUR")
    duration_days = Column(Integer, nullable=False, default=30)
    active = Column(Boolean, default=True)

    # к какому проекту (каналу) относится тариф
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)


# 👇 чтобы работали оба импорта:
# from app.models.plan import SubscriptionPlan
# и from app.models.plan import Plan
Plan = SubscriptionPlan

