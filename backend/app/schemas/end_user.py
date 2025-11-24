from pydantic import BaseModel


class EndUserBase(BaseModel):
    telegram_id: int
    language: str = "en"


class EndUserCreate(EndUserBase):
    pass


class EndUserRead(EndUserBase):
    id: int

    class Config:
        from_attributes = True
