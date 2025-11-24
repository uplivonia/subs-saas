from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.plan import SubscriptionPlan
from app.models.project import Project
from app.schemas.plan import PlanCreate, PlanRead

router = APIRouter()


@router.get("/project/{project_id}", response_model=List[PlanRead])
def list_plans_for_project(project_id: int, db: Session = Depends(get_db)):
    """
    Список активных тарифов для конкретного проекта (канала).
    """
    plans = (
        db.query(SubscriptionPlan)
        .filter(
            SubscriptionPlan.project_id == project_id,
            SubscriptionPlan.active == True,  # noqa: E712
        )
        .all()
    )
    return plans


@router.post("/", response_model=PlanRead)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    """
    Создать тарифный план для проекта.
    """
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")

    plan = SubscriptionPlan(
        project_id=payload.project_id,
        name=payload.name,
        price=payload.price,
        currency=payload.currency,
        duration_days=payload.duration_days,
        active=payload.active,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.get("/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan