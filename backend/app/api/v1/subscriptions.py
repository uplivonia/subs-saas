from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.end_user import EndUser
from app.models.subscription import Subscription
from app.models.plan import SubscriptionPlan
from app.models.project import Project
from app.schemas.subscription import SubscriptionRead, SubscriptionFromPlanCreate

router = APIRouter()


# ================================================================
#   СОЗДАНИЕ ПОДПИСКИ ПО ПЛАНУ (использовалось раньше)
# ================================================================
@router.post("/from-plan", response_model=SubscriptionRead)
def create_subscription_from_plan(
    payload: SubscriptionFromPlanCreate,
    db: Session = Depends(get_db),
):
    # 1. Найти или создать EndUser по telegram_id
    end_user = (
        db.query(EndUser)
        .filter(EndUser.telegram_id == payload.telegram_id)
        .first()
    )

    if not end_user:
        end_user = EndUser(
            telegram_id=payload.telegram_id,
            language=payload.language,
        )
        db.add(end_user)
        db.commit()
        db.refresh(end_user)

    # 2. Найти план
    plan = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.id == payload.plan_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=400, detail="Plan not found")

    # 3. Создать подписку
    now = datetime.utcnow()
    end_at = now + timedelta(days=plan.duration_days)

    subscription = Subscription(
        end_user_id=end_user.id,
        project_id=plan.project_id,
        plan_id=plan.id,
        start_at=now,
        end_at=end_at,
        status="active",
        auto_renew=False,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


# ================================================================
#   НОВЫЙ ВАЖНЕЙШИЙ ЭНДПОИНТ:
#   ПРОВЕРИТЬ АКТИВНУЮ ПОДПИСКУ ПО telegram_id + project_id
# ================================================================
@router.get("/active", response_model=SubscriptionRead)
def get_active_subscription_for_user(
    telegram_id: int,
    project_id: int,
    db: Session = Depends(get_db),
):
    """
    Вернуть активную подписку для пользователя в проекте.
    Активная = status='active' и end_at > сейчас.
    """

    now = datetime.utcnow()

    subscription = (
        db.query(Subscription)
        .join(EndUser, Subscription.end_user_id == EndUser.id)
        .filter(
            EndUser.telegram_id == telegram_id,
            Subscription.project_id == project_id,
            Subscription.status == "active",
            Subscription.end_at > now,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")

    return subscription
