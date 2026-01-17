"""
Endpoints utilisateur.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserWithContext

router = APIRouter()


@router.get("/me", response_model=UserWithContext)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère les informations de l'utilisateur courant avec ses groupes.
    
    Retourne les groupes de l'utilisateur pour l'état du frontend.
    """
    # Recharge l'utilisateur avec ses relations
    result = await db.execute(
        select(User)
        .options(selectinload(User.groups))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()
    
    return user
