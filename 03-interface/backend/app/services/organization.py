"""
CRUD operations for organization models (Service, Project).
"""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.organization import Service, Project
from app.models.user import User
from app.schemas.organization import ServiceCreate, ServiceUpdate, ProjectCreate, ProjectUpdate


# ============================================================
# Service CRUD
# ============================================================

async def get_service(db: AsyncSession, service_id: int) -> Optional[Service]:
    """Get a service by ID."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    return result.scalar_one_or_none()


async def get_service_by_name(db: AsyncSession, name: str) -> Optional[Service]:
    """Get a service by name."""
    result = await db.execute(select(Service).where(Service.name == name))
    return result.scalar_one_or_none()


async def get_services(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Service]:
    """Get all services."""
    result = await db.execute(
        select(Service)
        .offset(skip)
        .limit(limit)
        .order_by(Service.name)
    )
    return list(result.scalars().all())


async def create_service(db: AsyncSession, service_in: ServiceCreate) -> Service:
    """Create a new service."""
    service = Service(**service_in.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


async def update_service(
    db: AsyncSession, 
    service: Service, 
    service_in: ServiceUpdate
) -> Service:
    """Update a service."""
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    await db.commit()
    await db.refresh(service)
    return service


async def delete_service(db: AsyncSession, service: Service) -> None:
    """Delete a service."""
    await db.delete(service)
    await db.commit()


# ============================================================
# Project CRUD
# ============================================================

async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    """Get a project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def get_project_by_name(db: AsyncSession, name: str) -> Optional[Project]:
    """Get a project by name."""
    result = await db.execute(select(Project).where(Project.name == name))
    return result.scalar_one_or_none()


async def get_projects(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True
) -> List[Project]:
    """Get all projects."""
    query = select(Project).offset(skip).limit(limit).order_by(Project.name)
    if active_only:
        query = query.where(Project.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_projects(db: AsyncSession, user: User) -> List[Project]:
    """Get projects for a specific user."""
    result = await db.execute(
        select(Project)
        .join(Project.members)
        .where(User.id == user.id)
        .where(Project.is_active == True)
        .order_by(Project.name)
    )
    return list(result.scalars().all())


async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
    """Create a new project."""
    project = Project(**project_in.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession, 
    project: Project, 
    project_in: ProjectUpdate
) -> Project:
    """Update a project."""
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    """Delete a project."""
    await db.delete(project)
    await db.commit()


# ============================================================
# Membership management
# ============================================================

async def add_user_to_project(
    db: AsyncSession, 
    user: User, 
    project: Project
) -> None:
    """Add a user to a project."""
    if project not in user.projects:
        user.projects.append(project)
        await db.commit()


async def remove_user_from_project(
    db: AsyncSession, 
    user: User, 
    project: Project
) -> None:
    """Remove a user from a project."""
    if project in user.projects:
        user.projects.remove(project)
        await db.commit()
