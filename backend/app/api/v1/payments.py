from fastapi import APIRouter, HTTPException
from app.core.stripe_config import create_checkout_session

router = APIRouter()

@router.post("/stripe/session")
async def create_stripe_session(plan_id: int, project_id: int, amount: float, currency: str = "EUR"):
    try:
        session = create_checkout_session(amount, currency, plan_id, project_id)
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
