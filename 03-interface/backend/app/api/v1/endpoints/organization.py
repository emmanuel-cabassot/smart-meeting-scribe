"""
API endpoints for organization management (Services, Projects).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, get_current_active_superuser
from app.models.user import User
from app.schemas.organization import (
    ServiceRead, ServiceCreate, ServiceUpdate,
    ProjectRead, ProjectCreate, ProjectUpdate
)
from app.services import organization as org_service

router = APIRouter()


# ============================================================
# Services Endpoints
# ============================================================

@router.get("/services", response_model=List[ServiceRead])
async def list_services(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """List all services."""
    services = await org_service.get_services(db, skip=skip, limit=limit)
    return services


@router.get("/services/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific service."""
    service = await org_service.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_in: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),  # Admin only
):
    """Create a new service (admin only)."""
    existing = await org_service.get_service_by_name(db, service_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Service already exists")
    return await org_service.create_service(db, service_in)


@router.patch("/services/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),  # Admin only
):
    """Update a service (admin only)."""
    service = await org_service.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return await org_service.update_service(db, service, service_in)


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),  # Admin only
):
    """Delete a service (admin only)."""
    service = await org_service.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    await org_service.delete_service(db, service)


# ============================================================
# Projects Endpoints
# ============================================================

@router.get("/projects", response_model=List[ProjectRead])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
):
    """List all projects (or only user's projects based on query param)."""
    projects = await org_service.get_projects(db, skip=skip, limit=limit, active_only=active_only)
    return projects


@router.get("/projects/me", response_model=List[ProjectRead])
async def list_my_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List projects the current user is a member of."""
    projects = await org_service.get_user_projects(db, current_user)
    return projects


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific project."""
    project = await org_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),  # Admin only
):
    """Create a new project (admin only)."""
    existing = await org_service.get_project_by_name(db, project_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Project already exists")
    return await org_service.create_project(db, project_in)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),  # Admin only
):
    """Update a project (admin only)."""
    project = await org_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await org_service.update_project(db, project, project_in)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),  # Admin only
):
    """Delete a project (admin only)."""
    project = await org_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await org_service.delete_project(db, project)


# ============================================================
# Membership Management (Admin only)
# ============================================================

@router.post("/projects/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_member_to_project(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """Add a user to a project (admin only)."""
    from sqlalchemy import select
    from app.models.user import User as UserModel
    
    project = await org_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await org_service.add_user_to_project(db, user, project)


@router.delete("/projects/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_project(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """Remove a user from a project (admin only)."""
    from sqlalchemy import select
    from app.models.user import User as UserModel
    
    project = await org_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await org_service.remove_user_from_project(db, user, project)
