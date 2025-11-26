from pydantic import BaseModel


class ProjectBase(BaseModel):
    # ❗ Делаем опциональным, чтобы можно было создать проект без канала
    telegram_channel_id: int | None = None
    title: str | None = None
    username: str | None = None
    active: bool = True


class ProjectCreate(ProjectBase):
    # telegram_id автора, который создаёт этот проект
    owner_telegram_id: int


class ProjectRead(ProjectBase):
    id: int
    user_id: int
    # чтобы с фронта можно было получить connection_code и status,
    # которые мы положим в JSONB settings
    settings: dict | None = None

    class Config:
        from_attributes = True
