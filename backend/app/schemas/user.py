from pydantic import BaseModel

class UserBase(BaseModel):
    telegram_id: int
    name: str | None = None
    username: str | None = None
    language: str = "en"


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int

    # NEW — Stripe fields
    stripe_account_id: str | None = None
    stripe_onboarded: bool = False

    class Config:
        from_attributes = True
