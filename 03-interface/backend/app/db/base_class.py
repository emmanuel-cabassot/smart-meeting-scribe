"""
Classe de base pour les modèles SQLAlchemy.
Fournit des fonctionnalités communes et des conventions de nommage.
"""
from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    """
    Classe de base personnalisée qui fournit :
    - Génération automatique du nom de table (snake_case depuis le nom de classe)
    - Possibilité d'ajouter un pattern ID commun ici
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Génère le nom de table depuis le nom de classe (CamelCase -> snake_case)."""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


Base = declarative_base(cls=CustomBase)
