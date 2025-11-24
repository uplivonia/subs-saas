from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency для FastAPI: открывает сессию к БД и закрывает её после запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()