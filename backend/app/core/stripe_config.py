import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    amount: float,
    currency: str,
    plan_id: int,
    project_id: int,
    telegram_id: int,
):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {"name": f"Subscription Plan #{plan_id}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=(
            f"{settings.BACKEND_PUBLIC_URL}"
            f"/api/v1/payments/stripe/success?session_id={{CHECKOUT_SESSION_ID}}"
        ),
        cancel_url=f"{settings.BACKEND_PUBLIC_URL}/api/v1/payments/stripe/cancel",
        metadata={
            "plan_id": str(plan_id),
            "project_id": str(project_id),
            "telegram_id": str(telegram_id),
        },
    )
    return session
