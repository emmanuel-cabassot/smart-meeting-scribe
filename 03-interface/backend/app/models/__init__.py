"""
Models package - Import all models for Alembic to detect.
"""
from app.db.base_class import Base

# Import all models here so Alembic can detect them
from app.models.user import User
from app.models.meeting import Meeting
from app.models.organization import Service, Project

# Export for convenience
__all__ = ["Base", "User", "Meeting", "Service", "Project"]
