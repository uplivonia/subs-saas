from pydantic import BaseModel


class ProjectBase(BaseModel):
    # channel can be empty at first (we connect it later)
    telegram_channel_id: int | None = None
    title: str | None = None
    username: str | None = None
    active: bool = True


class ProjectCreate(ProjectBase):
    # This field is no longer required.
    # Backend determines the owner from JWT token (Authorization header),
    # so owner_telegram_id is optional and can be omitted in the request body.
    owner_telegram_id: int | None = None


class ProjectRead(ProjectBase):
    id: int
    user_id: int
    # frontend can read connection_code and status from settings
    settings: dict | None = None

    class Config:
        from_attributes = True
