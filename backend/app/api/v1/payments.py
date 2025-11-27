from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.stripe_config import create_checkout_session
from app.core.config import settings
from app.db.session import get_db
from app.models.payment import Payment
from app.models.end_user import EndUser
from app.models.subscription import Subscription
from app.models.plan import SubscriptionPlan
from app.models.user import User

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

        print(
            f"[WEBHOOK] ✅ Subscription created: {subscription.id} for user {payment.telegram_id}"
        )

    return {"received": True}


@router.get("/stripe/success")
async def stripe_success(session_id: str):
    return {"status": "ok", "session_id": session_id}


@router.get("/stripe/cancel")
async def stripe_cancel():
    return {"status": "canceled"}


# =========================================================
# STRIPE CONNECT: CREATOR PAYOUT ACCOUNT
# =========================================================

@router.post("/connect/link")
async def create_connect_link(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    # вот тут уже можно печатать
    print(">>> USING STRIPE KEY:", settings.STRIPE_SECRET_KEY[:10])

    """
    Creates or reuses a Stripe Express account for the current user
    and returns an onboarding link.
    """
    user = get_current_user_from_token(authorization, db)

    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="STRIPE_SECRET_KEY is not set")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # 1) Создаём Stripe Account, если его ещё нет
    if not user.stripe_account_id:
        try:
            account = stripe.Account.create(
                type="express",
            )
        except stripe.error.InvalidRequestError as e:
            # Это как раз тот случай "You can only create new accounts if..."
            print("Stripe Connect error while creating account:", e)
            raise HTTPException(
                status_code=400,
                detail="Stripe Connect is not enabled or not fully configured for this Stripe account. "
                       "Please double-check Connect settings and API key mode (test/live)."
            )
        except Exception as e:
            print("Stripe generic error while creating account:", e)
            raise HTTPException(
                status_code=400,
                detail=f"Stripe error while creating account: {str(e)}"
            )

        user.stripe_account_id = account.id
        db.commit()
        db.refresh(user)

    frontend_url = getattr(settings, "FRONTEND_URL", None) or "https://fanstero.netlify.app"
    frontend_url = frontend_url.rstrip("/")

    try:
        # 2) Создаём Account Link для онбординга
        account_link = stripe.AccountLink.create(
            account=user.stripe_account_id,
            refresh_url=f"{frontend_url}/app/settings",
            return_url=f"{frontend_url}/app/settings",
            type="account_onboarding",
        )
    except Exception as e:
        print("Stripe error while creating account link:", e)
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error while creating account link: {str(e)}"
        )

    return {"url": account_link["url"]}


@router.get("/connect/status")
async def connect_status(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Returns whether the current user has a connected Stripe account.
    Also, if we have an account but not onboarded yet,
    we check Stripe's `details_submitted` and update flag.
    """
    user = get_current_user_from_token(authorization, db)

    connected = bool(user.stripe_account_id and user.stripe_onboarded)

    # Попробуем обновить stripe_onboarded, если аккаунт есть, но флаг ещё False
    if user.stripe_account_id and not user.stripe_onboarded and settings.STRIPE_SECRET_KEY:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            account = stripe.Account.retrieve(user.stripe_account_id)
            if account.get("details_submitted", False):
                user.stripe_onboarded = True
                db.commit()
                connected = True
        except Exception as e:
            print("Stripe connect_status error:", e)

    return {
        "connected": connected,
        "stripe_account_id": user.stripe_account_id,
        "stripe_onboarded": user.stripe_onboarded,
    }
