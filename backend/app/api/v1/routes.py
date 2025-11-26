from fastapi import APIRouter

from app.api.v1 import projects, plans, users, subscriptions
from app.api.v1 import auth

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
