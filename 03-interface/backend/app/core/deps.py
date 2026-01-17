"""
Injection de dépendances pour les endpoints FastAPI.
Centralise les dépendances communes : session DB, utilisateur courant, etc.
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User

# Schéma OAuth2 pour l'extraction du token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance pour obtenir une session de base de données.
    Fournit une session et assure son nettoyage propre.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Récupère l'utilisateur authentifié depuis le token JWT.
    Lève une erreur 401 si le token est invalide ou l'utilisateur introuvable.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Récupère l'utilisateur depuis la base de données
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur inactif"
        )
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dépendance pour les endpoints réservés aux admins.
    Lève une erreur 403 si l'utilisateur n'est pas superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    return current_user
