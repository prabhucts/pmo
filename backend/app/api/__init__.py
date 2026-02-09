"""
API Routes
"""
from fastapi import APIRouter
from app.api import chat, projects, insights, uploads, rules, dashboard, templates

api_router = APIRouter()

# Include sub-routers
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["Data Upload"])
api_router.include_router(rules.router, prefix="/rules", tags=["Business Rules"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
