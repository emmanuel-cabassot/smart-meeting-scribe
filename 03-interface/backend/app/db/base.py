"""
Import de tous les modèles pour Alembic.
Ce fichier est utilisé par Alembic pour découvrir tous les modèles.
"""
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.meeting import Meeting  # noqa
from app.models.group import Group  # noqa
