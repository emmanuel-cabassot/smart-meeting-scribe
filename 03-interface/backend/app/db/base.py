"""
Import Base and all models here for Alembic to detect.
This file is the single source of truth for SQLAlchemy metadata.
"""
# Import the Base class
from app.db.base_class import Base

# Import all models to register them with Base.metadata
# This is required for Alembic autogenerate to work
from app.models.user import User
from app.models.meeting import Meeting
from app.models.organization import Service, Project

# Re-export Base for backward compatibility
__all__ = ["Base"]
