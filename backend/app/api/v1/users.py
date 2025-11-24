from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_or_get_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Проверяем — есть ли пользователь с таким telegram_id
    user = db.query(User).filter(User.telegram_id == payload.telegram_id).first()

    # Если есть — отдаём его
    if user:
        return user

    # Иначе создаём
    new_user = User(
        telegram_id=payload.telegram_id,
        name=payload.name,
        username=payload.username,
        language=payload.language or "en",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
