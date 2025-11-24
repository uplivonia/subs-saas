from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SubscriptionPlan(Base):
    __tablename__ = "plans"  # <--- ВАЖНО: имя таблицы plans

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="EUR")
    duration_days = Column(Integer, nullable=False, default=30)
    active = Column(Boolean, default=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship(
        "Project",
        backref="plans",   # <-- вместо back_populates
        lazy="joined",
    )
    subscriptions = relationship("Subscription", back_populates="plan")


# чтобы работали оба импорта:
#   from app.models.plan import SubscriptionPlan
#   from app.models.plan import Plan
Plan = SubscriptionPlan
