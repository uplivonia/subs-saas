from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.routes import api_router
from app.api.v1 import payments

# 👉 новые важные импорты
from app.db.base_class import Base
from app.db.session import engine
from app.models import user, project, plan, subscription, payment, end_user  # noqa: F401


# 👉 здесь один раз создаём все таблицы, если их нет
Base.metadata.create_all(bind=engine)


app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])


@app.get("/")
async def root():
    return {"status": "ok", "name": settings.PROJECT_NAME}
