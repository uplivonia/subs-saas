from fastapi.responses import RedirectResponse
from app.core.security import create_access_token

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

    # Редиректим обратно на frontend
    FRONTEND_URL = "https://fanstero.netlify.app/app"

    return RedirectResponse(url=f"{FRONTEND_URL}?token={token}")
