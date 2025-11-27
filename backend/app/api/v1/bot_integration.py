from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.connect_session import ConnectSession
from app.models.project import Project
from app.models.user import User

router = APIRouter()


class ChannelConnectedPayload(BaseModel):
    connect_token: str
    telegram_user_id: int
    channel_id: int
    channel_title: str | None = None
    channel_username: str | None = None


@router.post("/channel-connected")
def channel_connected(payload: ChannelConnectedPayload, db: Session = Depends(get_db)):
    """
    Called by the Telegram bot when it has been added as an admin
    to a channel for a specific connect_token.
    """

    session = (
        db.query(ConnectSession)
        .filter(ConnectSession.token == payload.connect_token)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Connect session not found")

    if session.expires_at and session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Connect session has expired")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # mark session as completed and save telegram_user_id
    session.telegram_user_id = payload.telegram_user_id
    session.is_completed = True

    # create project linked to this channel
    project = Project(
        user_id=user.id,
        telegram_channel_id=payload.channel_id,
        title=payload.channel_title or "Untitled channel",
        username=payload.channel_username,
        active=True,
        settings={},
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "ok": True,
        "project_id": project.id,
        "channel_id": payload.channel_id,
        "title": project.title,
    }
