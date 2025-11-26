from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
import secrets
from pydantic import BaseModel

from app.core.deps import get_db
from app.core.config import settings
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()


# ==== Дополнительная схема для привязки канала через бота ====

class ConnectChannelPayload(BaseModel):
    connection_code: str
    telegram_channel_id: int
    channel_title: str | None = None


# ==== Список проектов ====

@router.get("/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """Пока общий список всех проектов (для отладки/Channels страницы)."""
    projects = db.query(Project).all()
    return projects


# ==== Проверка, что бот админ (можем оставить для "Check connection" по желанию) ====

@router.get("/{project_id}/check_bot")
def check_bot_status(project_id: int, db: Session = Depends(get_db)):
    """
    Проверяем, добавлен ли бот в админы канала.
    """
    bot_token = settings.BOT_TOKEN
    if not bot_token or bot_token == "CHANGE_ME":
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.telegram_channel_id:
        return {"ok": False, "error": "Channel not configured"}

    chat_id = project.telegram_channel_id

    # Получаем ID бота
    me_resp = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe").json()
    bot_id = me_resp.get("result", {}).get("id")
    if not bot_id:
        return {"ok": False, "error": "Cannot get bot id", "response": me_resp}

    # Проверяем статус бота в канале
    resp = requests.get(
        f"https://api.telegram.org/bot{bot_token}/getChatMember",
        params={"chat_id": chat_id, "user_id": bot_id},
    ).json()

    status = resp.get("result", {}).get("status")
    if status in ("administrator", "creator"):
        return {"ok": True}

    return {"ok": False, "response": resp}


# ==== STEP 1: создать проект (без канала) ====

@router.post("/", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """
    Step 1: создать проект (платный канал) и привязать к автору по owner_telegram_id.
    Пока канал не привязан, telegram_channel_id = NULL.
    В settings кладём connection_code и status.
    """
    # Находим автора по telegram_id
    user = db.query(User).filter(User.telegram_id == payload.owner_telegram_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User with this telegram_id not found")

    # Генерируем короткий код, который будем использовать в deep-link
    connection_code = secrets.token_hex(3)  # типа "a3f1c2"

    settings_dict = {
        "connection_code": connection_code,
        "status": "pending",
    }

    project = Project(
        user_id=user.id,
        telegram_channel_id=None,  # пока не знаем
        title=payload.title,
        username=None,
        active=payload.active,
        settings=settings_dict,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ==== STEP 2: бот привязывает приватный канал по connection_code ====

@router.post("/connect-channel")
def connect_channel(
    payload: ConnectChannelPayload,
    db: Session = Depends(get_db),
):
    """
    Вызывается ботом, когда его добавили в приватный канал:
    /start connect_<connection_code>

    Мы:
    - находим Project по connection_code (в settings)
    - сохраняем telegram_channel_id
    - обновляем status = "connected"
    """
    code = payload.connection_code
    chat_id = payload.telegram_channel_id
    title = payload.channel_title

    project = (
        db.query(Project)
        .filter(Project.settings["connection_code"].astext == code)
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Invalid connection code")

    # Обновляем проект
    project.telegram_channel_id = chat_id
    if title:
        project.title = title

    settings_dict = project.settings or {}
    settings_dict["status"] = "connected"
    project.settings = settings_dict

    db.commit()
    db.refresh(project)

    return {"ok": True, "project_id": project.id}


# ==== Получить один проект ====

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
