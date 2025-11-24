from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


@router.get("/by_owner/{telegram_id}", response_model=List[ProjectRead])
def list_projects_by_owner(telegram_id: int, db: Session = Depends(get_db)):
    """
    Вернуть все проекты, привязанные к автору с данным telegram_id.
    Это то, что потом будет отображаться в его web-панели.
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return []

    projects = db.query(Project).filter(Project.user_id == user.id).all()
    return projects


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