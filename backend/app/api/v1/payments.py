from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.stripe_config import create_checkout_session
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment
from app.models.end_user import EndUser
from app.models.subscription import Subscription
from app.models.plan import SubscriptionPlan
from app.models.user import User
from app.models.project import Project

import stripe
from jose import jwt, JWTError

router = APIRouter()

ALGORITHM = "HS256"


# =========================================================
# Helper: get current User from JWT token (Authorization)
# =========================================================
def get_current_user_from_token(authorization: str | None, db: Session) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ---------------------------
# СОЗДАНИЕ STRIPE SESSION
# ---------------------------
@router.post("/stripe/session")
async def create_stripe_session(
    plan_id: int,
    project_id: int,
    amount: float,
    currency: str = "EUR",
    telegram_id: int = 0,
    db: Session = Depends(get_db),
):
    if telegram_id == 0:
        raise HTTPException(status_code=400, detail="telegram_id is required")

    try:
        session = create_checkout_session(
            amount=amount,
            currency=currency,
            plan_id=plan_id,
            project_id=project_id,
            telegram_id=telegram_id,
        )

        payment = Payment(
            telegram_id=telegram_id,
            plan_id=plan_id,
            project_id=project_id,
            stripe_session_id=session.id,
            amount=amount,
            currency=currency,
            status="pending",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {"checkout_url": session.url, "payment_id": payment.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------
# STRIPE WEBHOOK
# ---------------------------
@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500, detail="STRIPE_WEBHOOK_SECRET is not set"
        )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    # ============================================================
    # ОБРАБОТКА СОБЫТИЯ УСПЕШНОЙ ОПЛАТЫ
    # ============================================================
    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        session_id = session_obj["id"]

        # --- 1. ИЩЕМ ПЛАТЁЖ ---
        payment: Payment | None = (
            db.query(Payment)
            .filter(Payment.stripe_session_id == session_id)
            .first()
        )

        # Платёж должны были создать ДО оплаты — если нет, создаём аварийно
        if payment is None:
            metadata = session_obj.get("metadata", {})
            payment = Payment(
                telegram_id=int(metadata.get("telegram_id", 0)),
                plan_id=int(metadata.get("plan_id", 0)) or None,
                project_id=int(metadata.get("project_id", 0)) or None,
                stripe_session_id=session_id,
                amount=session_obj["amount_total"] / 100.0,
                currency=session_obj["currency"].upper(),
                status="paid",
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
        else:
            # если уже "paid" — значит вебхук повторился, ничего не делаем
            if payment.status == "paid":
                print(f"[WEBHOOK] ⚠ Payment {payment.id} already processed, skipping.")
                return {"received": True}

            payment.status = "paid"
            db.commit()
            db.refresh(payment)

        # --- 2. СОЗДАЁМ EndUser, если нет ---
        end_user = (
            db.query(EndUser)
            .filter(EndUser.telegram_id == payment.telegram_id)
            .first()
        )

        if not end_user:
            end_user = EndUser(
                telegram_id=payment.telegram_id,
                language="en",
            )
            db.add(end_user)
            db.flush()  # чтобы получить end_user.id

        # --- 3. ПОЛУЧАЕМ ПЛАН ---
        plan = (
            db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.id == payment.plan_id)
            .first()
        )

        if not plan:
            print(f"[WEBHOOK] ❌ Plan not found for payment {payment.id}")
            return {"received": True}

        now = datetime.utcnow()

        # Проверяем, нет ли уже активной подписки этого юзера на этот проект/план
        existing_sub = (
            db.query(Subscription)
            .filter(
                Subscription.end_user_id == end_user.id,
                Subscription.project_id == plan.project_id,
                Subscription.plan_id == plan.id,
                Subscription.status == "active",
                Subscription.end_at >= now,
            )
            .first()
        )

        if existing_sub:
            print(
                f"[WEBHOOK] ⚠ Subscription already active "
                f"(id={existing_sub.id}) for user {end_user.id}, skipping duplicate."
            )
            return {"received": True}

        # --- 4. СОЗДАЁМ ПОДПИСКУ ---
        duration = plan.duration_days or 30
        end_at = now + timedelta(days=duration)

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

        # --- 5. НАЧИСЛЯЕМ ДЕНЬГИ АВТОРУ ПРОЕКТА ---
        project = (
            db.query(Project)
            .filter(Project.id == plan.project_id)
            .first()
        )

        if not project:
            print(f"[WEBHOOK] ❌ Project not found for plan {plan.id}")
            db.commit()
            return {"received": True}

        creator = (
            db.query(User)
            .filter(User.id == project.user_id)
            .first()
        )

        if not creator:
            print(f"[WEBHOOK] ❌ Creator not found for project {project.id}")
            db.commit()
            return {"received": True}

        # Сколько отдаём автору? например 85% от суммы
        platform_fee_pct = Decimal("0.15")
        gross_amount = Decimal(str(payment.amount))  # например 9.99
        creator_amount = gross_amount * (Decimal("1.0") - platform_fee_pct)

        # в центы
        creator_cents = int(creator_amount * 100)

        creator.balance_cents = (creator.balance_cents or 0) + creator_cents

        db.commit()

        print(
            f"[WEBHOOK] ✅ Subscription {subscription.id} created for user {payment.telegram_id}; "
            f"credited {creator_amount} to creator {creator.id}. "
            f"New balance: {creator.balance_cents / 100:.2f}."
        )

    return {"received": True}


@router.get("/stripe/success")
async def stripe_success(session_id: str):
    return {"status": "ok", "session_id": session_id}


@router.get("/stripe/cancel")
async def stripe_cancel():
    return {"status": "canceled"}


# =========================================================
# STRIPE CONNECT: CREATOR PAYOUT ACCOUNT (ПОКА НЕ ИСПОЛЬЗУЕМ)
# =========================================================
# Эти endpoints можно оставить на будущее, но на фронте их НЕ вызываем.
# Текущая логика — один общий бизнес-аккаунт Stripe, а авторам идёт
# внутренний баланс + ручные выплаты.
@router.post("/connect/link")
async def create_connect_link(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    raise HTTPException(status_code=400, detail="Stripe Connect is not used in this version.")


@router.get("/connect/status")
async def connect_status(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    return {
        "connected": False,
        "stripe_account_id": None,
        "stripe_onboarded": False,
    }
