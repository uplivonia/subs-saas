from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.user import User


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ⭐ ДЕЛАЕМ nullable=True — это критично для приватных каналов
    telegram_channel_id = Column(BigInteger, nullable=True, index=True)

    title = Column(String, nullable=True)
    username = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    settings = Column(JSONB, default=dict)

    owner = relationship(User, backref="projects")
