import hashlib
import hmac
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()  # <-- ВАЖНО: объявляем router до использования


def verify_telegram_auth(data: Dict[str, str]) -> bool:
    """Проверка подписи Telegram Login Widget."""
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    # data_check_string по правилам Telegram:
    # https://core.telegram.org/widgets/login#checking-authorization
    pairs = [f"{k}={v}" for k, v in sorted(data.items())]
    data_check_string = "\n".join(pairs)

    secret_key = hashlib.sha256(settings.BOT_TOKEN.encode("utf-8")).digest()
    calc_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(calc_hash, received_hash)


@router.get("/telegram")
async def auth_telegram(request: Request, db: Session = Depends(get_db)):
    params = dict(request.query_params)

    if not verify_telegram_auth(params.copy()):
        raise HTTPException(status_code=400, detail="Invalid Telegram auth data")

    telegram_id = int(params["id"])

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        first_name = params.get("first_name") or ""
        last_name = params.get("last_name") or ""
        full_name = (first_name + " " + last_name).strip() or None

        user = User(
            telegram_id=telegram_id,
            name=full_name,
            username=params.get("username"),
            language="en",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # создаём JWT
    token = create_access_token({"sub": str(user.id)})

    # редиректим обратно на фронт
    FRONTEND_URL = "https://fanstero.netlify.app/app"

    return RedirectResponse(url=f"{FRONTEND_URL}?token={token}")
