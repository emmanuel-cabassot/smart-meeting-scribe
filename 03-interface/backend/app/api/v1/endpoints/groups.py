"""
Endpoints CRUD pour les Groupes.
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, get_current_active_superuser
from app.models.user import User
from app.models.group import Group
from app.schemas.group import GroupRead, GroupCreate, GroupUpdate, GroupMinimal
from app.services.group import (
    get_group,
    get_groups,
    get_user_groups,
    create_group,
    update_group,
    delete_group,
    add_user_to_group,
    remove_user_from_group,
)

router = APIRouter()


@router.get("/", response_model=List[GroupRead])
async def list_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Liste tous les groupes.
    """
    return await get_groups(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/me", response_model=List[GroupMinimal])
async def list_my_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Liste les groupes de l'utilisateur courant.
    """
    # Recharge l'utilisateur avec ses groupes
    result = await db.execute(
        select(User)
        .options(selectinload(User.groups))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()
    return user.groups


@router.get("/{group_id}", response_model=GroupRead)
async def get_group_detail(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère un groupe par son ID.
    """
    group = await get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    return group


@router.post("/", response_model=GroupRead)
async def create_group_endpoint(
    group_in: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Crée un nouveau groupe (admin seulement).
    """
    # Vérifie que le nom n'existe pas déjà
    from app.services.group import get_group_by_name
    existing = await get_group_by_name(db, group_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Ce nom de groupe existe déjà")
    
    return await create_group(db, group_in)


@router.patch("/{group_id}", response_model=GroupRead)
async def update_group_endpoint(
    group_id: int,
    group_in: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Met à jour un groupe (admin seulement).
    """
    group = await get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    
    return await update_group(db, group, group_in)


@router.delete("/{group_id}", status_code=204)
async def delete_group_endpoint(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Supprime un groupe (admin seulement).
    """
    group = await get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    
    await delete_group(db, group)
    return None


# ============================================================
# Gestion des membres
# ============================================================

@router.post("/{group_id}/members/{user_id}", status_code=201)
async def add_member_to_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Ajoute un utilisateur à un groupe (admin seulement).
    """
    group = await get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    
    # Récupère l'utilisateur
    result = await db.execute(
        select(User)
        .options(selectinload(User.groups))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    await add_user_to_group(db, user, group)
    return {"message": f"Utilisateur {user.email} ajouté au groupe {group.name}"}


@router.delete("/{group_id}/members/{user_id}", status_code=204)
async def remove_member_from_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Retire un utilisateur d'un groupe (admin seulement).
    """
    group = await get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Groupe introuvable")
    
    # Récupère l'utilisateur
    result = await db.execute(
        select(User)
        .options(selectinload(User.groups))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    await remove_user_from_group(db, user, group)
    return None
