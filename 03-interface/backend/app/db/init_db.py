"""
Script d'initialisation de la base de données.
Crée les Groupes par défaut et le SuperUser au premier lancement.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.user import User
from app.models.group import Group, GroupType


# Groupes par défaut avec leurs types (valeurs string lowercase)
DEFAULT_GROUPS = [
    {"name": "Tous", "description": "Groupe par défaut - Tous les utilisateurs", "type": "department"},
    {"name": "Direction", "description": "Équipe de direction", "type": "department"},
    {"name": "R&D", "description": "Recherche & Développement", "type": "department"},
    {"name": "Marketing", "description": "Marketing & Communications", "type": "department"},
    {"name": "Commercial", "description": "Équipe commerciale", "type": "department"},
    {"name": "RH", "description": "Ressources Humaines", "type": "department"},
    {"name": "Finance", "description": "Finance & Comptabilité", "type": "department"},
    # Exemples de groupes projets/récurrents
    {"name": "COMOP", "description": "Comité opérationnel hebdomadaire", "type": "recurring"},
    {"name": "Café AGAM", "description": "Présentation hebdomadaire", "type": "recurring"},
]

# Configuration SuperUser
FIRST_SUPERUSER_EMAIL = "admin@example.com"
FIRST_SUPERUSER_PASSWORD = "admin123"  # Changer en production !


async def init_groups(db: AsyncSession) -> dict[str, Group]:
    """Crée les groupes par défaut s'ils n'existent pas."""
    groups = {}
    
    for group_data in DEFAULT_GROUPS:
        result = await db.execute(
            select(Group).where(Group.name == group_data["name"])
        )
        group = result.scalar_one_or_none()
        
        if not group:
            group = Group(**group_data)
            db.add(group)
            print(f"✅ Groupe créé : {group_data['name']}")
        else:
            print(f"ℹ️  Groupe existant : {group_data['name']}")
        
        groups[group_data["name"]] = group
    
    await db.commit()
    return groups


async def init_superuser(
    db: AsyncSession, 
    default_groups: list[Group]
) -> User:
    """Crée le superuser s'il n'existe pas et l'assigne aux groupes."""
    result = await db.execute(
        select(User).where(User.email == FIRST_SUPERUSER_EMAIL)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(FIRST_SUPERUSER_PASSWORD),
            is_active=True,
            is_superuser=True,
        )
        # Ajoute les groupes par défaut au superuser
        user.groups = default_groups
        db.add(user)
        await db.commit()
        print(f"✅ SuperUser créé : {FIRST_SUPERUSER_EMAIL}")
    else:
        print(f"ℹ️  SuperUser existant : {FIRST_SUPERUSER_EMAIL}")
    
    return user


async def init_db(db: AsyncSession) -> None:
    """
    Fonction principale d'initialisation.
    Appelée au démarrage de l'application.
    """
    print("\n🚀 Initialisation de la base de données...")
    
    # 1. Créer les Groupes
    groups = await init_groups(db)
    
    # 2. Créer le SuperUser (assigné à Tous + Direction)
    await init_superuser(
        db, 
        default_groups=[groups["Tous"], groups["Direction"]]
    )
    
    print("✅ Initialisation terminée !\n")
