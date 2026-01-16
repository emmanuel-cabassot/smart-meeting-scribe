"""
Base class for SQLAlchemy models.
Provides common functionality and naming conventions.
"""
from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    """
    Custom base class that provides:
    - Automatic table name generation (snake_case from class name)
    - Common ID pattern can be added here
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name (CamelCase -> snake_case)."""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


Base = declarative_base(cls=CustomBase)
