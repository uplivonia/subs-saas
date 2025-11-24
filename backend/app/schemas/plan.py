from pydantic import BaseModel
from decimal import Decimal


class PlanBase(BaseModel):
    name: str
    price: Decimal
    currency: str = "EUR"
    duration_days: int
    active: bool = True


class PlanCreate(PlanBase):
    project_id: int


class PlanRead(PlanBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True
