from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.stripe_config import create_checkout_session
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment
from app.models.end_user import EndUser
from app.models.subscription import Subscription
from app.models.plan import SubscriptionPlan

import stripe

router = APIRouter()


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
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET is not set")

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
        else:
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

        # --- 4. СОЗДАЁМ ПОДПИСКУ ---
        now = datetime.utcnow()
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
        db.commit()

        print(f"[WEBHOOK] ✅ Subscription created: {subscription.id} for user {payment.telegram_id}")

    return {"received": True}


@router.get("/stripe/success")
async def stripe_success(session_id: str):
    return {"status": "ok", "session_id": session_id}


@router.get("/stripe/cancel")
async def stripe_cancel():
    return {"status": "canceled"}
