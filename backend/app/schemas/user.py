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

    class Config:
        from_attributes = True
