from pydantic import BaseModel


class ProjectBase(BaseModel):
    telegram_channel_id: int
    title: str | None = None
    username: str | None = None
    active: bool = True


class ProjectCreate(ProjectBase):
    # telegram_id автора, который создаёт этот проект
    owner_telegram_id: int


class ProjectRead(ProjectBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
