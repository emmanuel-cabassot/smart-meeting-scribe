"""
User endpoints.
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
    Get current user info with organization context.
    
    Returns the user's service and projects for frontend state.
    """
    # Reload user with relationships
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.service),
            selectinload(User.projects)
        )
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()
    
    return user
