"""
Database initialization script.
Creates default Services, Projects, and SuperUser on first run.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.user import User
from app.models.organization import Service, Project


# Default data for seeding
DEFAULT_SERVICES = [
    {"name": "R&D", "description": "Research & Development"},
    {"name": "Sales", "description": "Sales & Business Development"},
    {"name": "Marketing", "description": "Marketing & Communications"},
    {"name": "HR", "description": "Human Resources"},
    {"name": "Finance", "description": "Finance & Accounting"},
]

DEFAULT_PROJECTS = [
    {"name": "Lancement V5", "description": "Nouvelle version majeure du produit"},
    {"name": "Audit Sécurité", "description": "Audit de sécurité annuel"},
]

# SuperUser configuration
FIRST_SUPERUSER_EMAIL = "admin@example.com"
FIRST_SUPERUSER_PASSWORD = "admin123"  # Change in production!


async def init_services(db: AsyncSession) -> dict[str, Service]:
    """Create default services if they don't exist."""
    services = {}
    
    for service_data in DEFAULT_SERVICES:
        result = await db.execute(
            select(Service).where(Service.name == service_data["name"])
        )
        service = result.scalar_one_or_none()
        
        if not service:
            service = Service(**service_data)
            db.add(service)
            print(f"✅ Created Service: {service_data['name']}")
        else:
            print(f"ℹ️  Service already exists: {service_data['name']}")
        
        services[service_data["name"]] = service
    
    await db.commit()
    return services


async def init_projects(db: AsyncSession) -> dict[str, Project]:
    """Create default projects if they don't exist."""
    projects = {}
    
    for project_data in DEFAULT_PROJECTS:
        result = await db.execute(
            select(Project).where(Project.name == project_data["name"])
        )
        project = result.scalar_one_or_none()
        
        if not project:
            project = Project(**project_data)
            db.add(project)
            print(f"✅ Created Project: {project_data['name']}")
        else:
            print(f"ℹ️  Project already exists: {project_data['name']}")
        
        projects[project_data["name"]] = project
    
    await db.commit()
    return projects


async def init_superuser(
    db: AsyncSession, 
    default_service: Service,
    all_projects: list[Project]
) -> User:
    """Create superuser if doesn't exist, assign to R&D and all projects."""
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
            service_id=default_service.id,
        )
        # Add all projects to superuser
        user.projects = all_projects
        db.add(user)
        await db.commit()
        print(f"✅ Created SuperUser: {FIRST_SUPERUSER_EMAIL}")
    else:
        print(f"ℹ️  SuperUser already exists: {FIRST_SUPERUSER_EMAIL}")
    
    return user


async def init_db(db: AsyncSession) -> None:
    """
    Main initialization function.
    Call this on application startup.
    """
    print("\n🚀 Initializing database...")
    
    # 1. Create Services
    services = await init_services(db)
    
    # 2. Create Projects
    projects = await init_projects(db)
    
    # 3. Create SuperUser (assigned to R&D + all projects)
    await init_superuser(
        db, 
        default_service=services["R&D"],
        all_projects=list(projects.values())
    )
    
    print("✅ Database initialization complete!\n")
