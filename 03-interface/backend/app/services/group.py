"""
Opérations CRUD pour le modèle Group.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate


async def get_group(db: AsyncSession, group_id: int) -> Optional[Group]:
    """Récupère un groupe par son ID."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()


async def get_group_by_name(db: AsyncSession, name: str) -> Optional[Group]:
    """Récupère un groupe par son nom."""
    result = await db.execute(select(Group).where(Group.name == name))
    return result.scalar_one_or_none()


async def get_groups(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True
) -> List[Group]:
    """Récupère tous les groupes."""
    query = select(Group).offset(skip).limit(limit).order_by(Group.name)
    if active_only:
        query = query.where(Group.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_groups(db: AsyncSession, user: User) -> List[Group]:
    """Récupère les groupes d'un utilisateur."""
    result = await db.execute(
        select(Group)
        .join(Group.members)
        .where(User.id == user.id)
        .where(Group.is_active == True)
        .order_by(Group.name)
    )
    return list(result.scalars().all())


async def create_group(db: AsyncSession, group_in: GroupCreate) -> Group:
    """Crée un nouveau groupe."""
    group = Group(**group_in.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def update_group(
    db: AsyncSession, 
    group: Group, 
    group_in: GroupUpdate
) -> Group:
    """Met à jour un groupe."""
    update_data = group_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    await db.commit()
    await db.refresh(group)
    return group


async def delete_group(db: AsyncSession, group: Group) -> None:
    """Supprime un groupe."""
    await db.delete(group)
    await db.commit()


# ============================================================
# Gestion des membres
# ============================================================

async def add_user_to_group(
    db: AsyncSession, 
    user: User, 
    group: Group
) -> None:
    """Ajoute un utilisateur à un groupe."""
    if group not in user.groups:
        user.groups.append(group)
        await db.commit()


async def remove_user_from_group(
    db: AsyncSession, 
    user: User, 
    group: Group
) -> None:
    """Retire un utilisateur d'un groupe."""
    if group in user.groups:
        user.groups.remove(group)
        await db.commit()
