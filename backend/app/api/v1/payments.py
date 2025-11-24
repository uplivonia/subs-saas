from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.core.stripe_config import create_checkout_session
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment

import stripe

router = APIRouter()


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


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        # На случай, если ещё не настроили webhook в Stripe
        raise HTTPException(status_code=500, detail="STRIPE_WEBHOOK_SECRET is not set")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        session_id = session_obj["id"]

        payment: Payment | None = (
            db.query(Payment)
            .filter(Payment.stripe_session_id == session_id)
            .first()
        )

        if payment is None:
            # На всякий случай создаём, если по какой-то причине не нашли
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

    # Можно обрабатывать и другие типы событий (payment_failed, refunded и т.п.)
    return {"received": True}


@router.get("/stripe/success")
async def stripe_success(session_id: str):
    # Пока просто заглушка
    return {"status": "ok", "session_id": session_id}


@router.get("/stripe/cancel")
async def stripe_cancel():
    return {"status": "canceled"}
