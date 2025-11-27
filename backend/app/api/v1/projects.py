from typing import List

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import requests
import secrets
from pydantic import BaseModel
from jose import jwt, JWTError

from app.core.deps import get_db
from app.core.config import settings
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()

ALGORITHM = "HS256"  # тот же, что использует твой бекенд при создании JWT


# ==== Дополнительная схема для привязки канала через бота ====

class ConnectChannelPayload(BaseModel):
    connection_code: str
    telegram_channel_id: int
    channel_title: str | None = None


# ==== Список проектов ====

@router.get("/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """Temporary: list all projects (for debugging / Channels page)."""
    projects = db.query(Project).all()
    return projects


# ==== Проверка, что бот админ (можем оставить для "Check connection" по желанию) ====

@router.get("/{project_id}/check_bot")
def check_bot_status(project_id: int, db: Session = Depends(get_db)):
    """
    Check if the bot is an administrator in the project's Telegram channel.
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

    # Get bot id
    me_resp = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe").json()
    bot_id = me_resp.get("result", {}).get("id")
    if not bot_id:
        return {"ok": False, "error": "Cannot get bot id", "response": me_resp}

    # Check bot status in channel
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
def create_project(
    payload: ProjectCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Step 1: create a project (paid channel) and link it to the owner.

    ❗ Owner is detected automatically from JWT token in Authorization header.
    We no longer rely on payload.owner_telegram_id.
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]

    # Decode JWT and extract user id from "sub"
    try:
        payload_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload_jwt.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Find user by internal id
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate short connection code that will be used in bot deep link
    connection_code = secrets.token_hex(3)  # e.g. "a3f1c2"

    settings_dict = {
        "connection_code": connection_code,
        "status": "pending",
    }

    project = Project(
        user_id=user.id,
        telegram_channel_id=None,  # not known yet
        title=payload.title,
        username=None,
        active=payload.active,
        settings=settings_dict,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ==== STEP 1.5: получить deep-link для привязки канала через бота ====

@router.post("/{project_id}/connect-link")
def get_project_connect_link(project_id: int, db: Session = Depends(get_db)):
    """
    Returns a Telegram deep link for the bot in the form:
    https://t.me/<bot_username>?start=connect_<connection_code>

    Frontend can call this endpoint when user clicks "Add channel"
    and then redirect the user to the returned URL.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    settings_dict = project.settings or {}

    # If connection_code is missing for some reason, generate it
    connection_code = settings_dict.get("connection_code")
    if not connection_code:
        connection_code = secrets.token_hex(3)
        settings_dict["connection_code"] = connection_code
        # If status is not set, mark as pending
        settings_dict.setdefault("status", "pending")
        project.settings = settings_dict
        db.commit()
        db.refresh(project)

    # Get bot username from settings or fallback to a default value
    bot_username = getattr(settings, "BOT_USERNAME", None) or "oneclicksub_bot"

    bot_link = f"https://t.me/{bot_username}?start=connect_{connection_code}"

    return {"bot_link": bot_link}


# ==== STEP 2: бот привязывает приватный канал по connection_code ====

@router.post("/connect-channel")
def connect_channel(
    payload: ConnectChannelPayload,
    db: Session = Depends(get_db),
):
    """
    Called by the bot when it has been added to a private channel
    after user used /start connect_<connection_code>.

    We:
    - find Project by connection_code stored in settings
    - save telegram_channel_id
    - update status = "connected"
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

    # Update project
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
