from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests

from app.core.deps import get_db
from app.core.config import settings
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()


@router.get("/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """Пока общий список всех проектов (для отладки)."""
    projects = db.query(Project).all()
    return projects


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

    # Пытаемся взять либо username, либо numeric chat_id
    if project.username:
        chat_id = project.username if project.username.startswith("@") else f"@{project.username}"
    elif project.telegram_channel_id:
        chat_id = project.telegram_channel_id
    else:
        return {"ok": False, "error": "Channel not configured"}

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


@router.post("/", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """
    Создать проект (канал) и привязать к автору по owner_telegram_id.
    """
    # Находим автора по telegram_id
    user = db.query(User).filter(User.telegram_id == payload.owner_telegram_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User with this telegram_id not found")

    project = Project(
        user_id=user.id,
        telegram_channel_id=payload.telegram_channel_id,
        title=payload.title,
        username=payload.username,
        active=payload.active,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
