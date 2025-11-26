from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends


from app.core.deps import get_db
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
async def check_bot_status(project_id: int, db: Session = Depends(get_db)):
    from app.core.config import settings
    import requests

    bot_token = settings.BOT_TOKEN
    if not bot_token or bot_token == "CHANGE_ME":
        return {"ok": False, "error": "BOT_TOKEN not configured"}

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {"ok": False, "error": "Project not found"}

    channel = project.channel_username
    if not channel:
        return {"ok": False, "error": "Channel username missing"}

    # Telegram API → getChatMember
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    params = {
        "chat_id": channel if channel.startswith("@") else f"@{channel}",
        "user_id": (await requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")).json()["result"]["id"]
    }

    r = requests.get(url, params=params).json()

    if "result" in r:
        status = r["result"]["status"]
        if status in ("administrator", "creator"):
            return {"ok": True}

    return {"ok": False, "response": r}


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