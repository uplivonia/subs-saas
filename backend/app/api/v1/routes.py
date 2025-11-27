from fastapi import APIRouter

from app.api.v1 import projects, plans, users, subscriptions
from app.api.v1 import auth
from app.api.v1 import bot_integration

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bot_integration.router, prefix="/bot", tags=["bot"])
