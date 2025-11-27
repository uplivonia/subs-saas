from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.user import User


class ConnectSession(Base):
    __tablename__ = "connect_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # токен, который мы зашиваем в deep link к боту
    token = Column(String, unique=True, index=True, nullable=False)

    # к какому web-пользователю относится эта сессия
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship(User, backref="connect_sessions")

    # телеграм-id автора (заполним, когда бот впервые от него напишет)
    telegram_user_id = Column(BigInteger, nullable=True, index=True)

    # отметка, что канал успешно привязан
    is_completed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
