from datetime import datetime
from pydantic import BaseModel


class SubscriptionBase(BaseModel):
    project_id: int
    plan_id: int
    start_at: datetime
    end_at: datetime
    status: str


class SubscriptionRead(SubscriptionBase):
    id: int
    end_user_id: int

    class Config:
        from_attributes = True


class SubscriptionFromPlanCreate(BaseModel):
    telegram_id: int
    language: str = "en"
    plan_id: int
