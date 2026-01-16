# 🧠 Logique Matricielle : Services & Projets

> **Objectif** : Transformer l'application "Mono-User" en plateforme "Entreprise" avec gestion des droits basée sur une double appartenance.

---

## 📋 Table des Matières

1. [Le Concept Matriciel](#-le-concept-matriciel)
2. [Modèle de Données](#-modèle-de-données)
3. [Algorithme de Visibilité](#-algorithme-de-visibilité)
4. [Décisions Architecturales](#-décisions-architecturales)
5. [Implémentation SQLAlchemy](#-implémentation-sqlalchemy)
6. [Roadmap](#-roadmap-dimplémentation)

---

## 🎯 Le Concept Matriciel

Le système repose sur une **double appartenance** pour casser les silos tout en gardant une hiérarchie claire.

### 🏢 LE SERVICE (Vertical / Structurel)

| Aspect | Description |
|--------|-------------|
| **C'est quoi ?** | La "Maison Mère" de l'utilisateur. C'est le département hiérarchique. |
| **Exemples** | R&D, Sales, Marketing, HR |
| **Règle** | Un Utilisateur appartient à **UN SEUL** Service principal (Relation `1:N`) |
| **Philosophie** | *"Dis-moi quel est ton métier."* |

### 🚀 LE PROJET (Transversal / Temporaire)

| Aspect | Description |
|--------|-------------|
| **C'est quoi ?** | Une mission qui regroupe des gens de **plusieurs services**. |
| **Exemples** | Lancement V5, Audit Sécurité, Hackathon 2026 |
| **Règle** | Un Utilisateur peut appartenir à **PLUSIEURS** Projets (Relation `N:N`) |
| **Philosophie** | *"Dis-moi sur quoi tu travailles actuellement."* |

---

## 📊 Modèle de Données

### Logique d'Appartenance (User)

Quand un utilisateur (ex: Emmanuel) se connecte, le système charge ses droits :

```json
{
  "identity": "Emmanuel",
  "service": "R&D",
  "projects": ["Lancement V5", "Audit Sécurité"]
}
```

### Logique de Propriété (Meeting)

| Attribut | Type | Description |
|----------|------|-------------|
| **service_id** | Obligatoire | Appartient automatiquement au Service de l'uploader |
| **projects** | Optionnel (M2M) | Peut être liée à plusieurs Projets |
| **is_confidential** | Boolean | Si `true`, visible uniquement par le Service (pas les Projets) |

### Schéma Technique

```
┌─────────────────────────────────────────────────────────────────────┐
│                           BASE DE DONNÉES                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐   │
│   │   SERVICE   │         │    USER     │         │   PROJECT   │   │
│   ├─────────────┤         ├─────────────┤         ├─────────────┤   │
│   │ id          │◄───────┐│ id          │┌───────►│ id          │   │
│   │ name        │    1:N ││ email       ││  N:N   │ name        │   │
│   │ description │        ││ service_id ─┘│        │ is_active   │   │
│   └─────────────┘        │└─────────────┘│        └─────────────┘   │
│         │                │       │       │               │          │
│         │                │       ▼       │               │          │
│         │                │ ┌───────────────────┐         │          │
│         │                │ │ user_project_link │◄────────┘          │
│         │                │ │ user_id | proj_id │                    │
│         │                │ └───────────────────┘                    │
│         │                │                                          │
│         ▼                │                      ┌─────────────────┐ │
│   ┌─────────────┐        │                      │meeting_proj_link│ │
│   │   MEETING   │        │                      │ meet_id | proj  │ │
│   ├─────────────┤        │                      └────────▲────────┘ │
│   │ id (UUID)   │        │                               │          │
│   │ title       │        │                               │          │
│   │ is_confid.  │        │                               │          │
│   │ owner_id   ─┼────────┘  (SET NULL on delete)         │          │
│   │ service_id ─┼───────────────────────────────────────►│          │
│   │ projects ───┼───────────────────────────────────────►│          │
│   └─────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

| Table | Relation | Explication |
|-------|----------|-------------|
| `User` | `service_id` (FK) | 1 User appartient à 1 Service |
| `User` | `projects` (M2M) | 1 User suit N Projets |
| `Meeting` | `service_id` (FK) | 1 Réunion appartient à 1 Service |
| `Meeting` | `projects` (M2M) | 1 Réunion concerne N Projets |
| `Meeting` | `owner_id` (FK, SET NULL) | Créateur (nullable si supprimé) |

---

## 🔐 Algorithme de Visibilité

### Règle Principale

Pour qu'un **Utilisateur U** voie une **Réunion M**, il faut :

```python
def can_access_meeting(user: User, meeting: Meeting) -> bool:
    # Condition A : Solidarité de Service
    if meeting.service_id == user.service_id:
        return True  # Même si confidentiel
    
    # Condition B : Passerelle Projet (si pas confidentiel)
    if not meeting.is_confidential:
        user_project_ids = {p.id for p in user.projects}
        meeting_project_ids = {p.id for p in meeting.projects}
        if user_project_ids & meeting_project_ids:  # Intersection non vide
            return True
    
    return False
```

### 💡 Exemple Concret

| Acteur | Service | Projets |
|--------|---------|---------|
| Emmanuel | R&D | Lancement V5, Audit Sécurité |
| Julie | Marketing | Lancement V5 |
| Marc | HR | ∅ |

**Scénario :** Emmanuel (R&D) upload un "Point Tech" et le tague "Projet V5".

| Réunion | is_confidential | Emmanuel (R&D) | Julie (Marketing) | Marc (HR) |
|---------|-----------------|----------------|-------------------|-----------|
| Point Tech | `false` | ✅ Service | ✅ Projet V5 | ❌ |
| Point Tech | `true` | ✅ Service | ❌ Bloqué | ❌ |

---

## 🛡️ Décisions Architecturales

Voici les règles définitives pour résoudre les cas limites :

### 1. Confidentialité (`is_confidential`)

> **Règle** : Si `true`, la réunion est visible **uniquement** par les membres du Service, même si elle est taguée sur un Projet.

```python
is_confidential = Column(Boolean, default=False, nullable=False)
```

### 2. Sécurité du Tagging

> **Règle** : Un utilisateur ne peut taguer une réunion que sur les projets **dont il est membre**.

```python
# API Validation
if project_id not in user.project_ids:
    raise HTTPException(403, "Vous n'êtes pas membre de ce projet")
```

### 3. Rôles et Permissions (V1 Simplifiée)

| Action | Qui peut ? |
|--------|------------|
| Voir une réunion | Membre du Service OU Membre d'un Projet lié |
| Créer une réunion | Tout utilisateur authentifié |
| Modifier une réunion | Créateur (`owner_id`) OU Admin global |
| Supprimer une réunion | Créateur (`owner_id`) OU Admin global |

> ⚠️ Les rôles fins (`admin`, `viewer`, `contributor`) seront ajoutés en **V2**.

### 4. Réunions Orphelines

> **Règle** : Si un utilisateur est supprimé, ses réunions **restent** dans le système.

```python
owner_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
```

### 5. Attribution du Service

> **Règle** : Le service est **automatiquement** celui de l'utilisateur. Pas de choix manuel (V1).

```python
meeting.service_id = current_user.service_id  # Automatique
```

---

## 💻 Implémentation SQLAlchemy

### Fichier : `models/organization.py`

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Table d'association : User <-> Project (N:N)
user_project_link = Table(
    "user_project_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("project.id"), primary_key=True),
)

# Table d'association : Meeting <-> Project (N:N)
meeting_project_link = Table(
    "meeting_project_link",
    Base.metadata,
    Column("meeting_id", String, ForeignKey("meeting.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("project.id"), primary_key=True),
)


class Service(Base):
    """Département vertical (R&D, Sales, Marketing...)"""
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Relations
    users = relationship("User", back_populates="service")
    meetings = relationship("Meeting", back_populates="service")


class Project(Base):
    """Mission transversale (Lancement V5, Audit Sécurité...)"""
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relations Many-to-Many
    members = relationship("User", secondary=user_project_link, back_populates="projects")
    meetings = relationship("Meeting", secondary=meeting_project_link, back_populates="projects")
```

### Fichier : `models/meeting.py` (Mise à jour)

```python
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base
from .organization import meeting_project_link


class Meeting(Base):
    __tablename__ = "meeting"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Confidentialité
    is_confidential = Column(Boolean, default=False, nullable=False)

    # Propriétaire (SET NULL si supprimé)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    owner = relationship("User", back_populates="meetings")

    # Service (obligatoire, automatique)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    service = relationship("Service", back_populates="meetings")

    # Projets (Many-to-Many, optionnel)
    projects = relationship("Project", secondary=meeting_project_link, back_populates="meetings")
```

### Fichier : `api/v1/endpoints/meetings.py` (Sécurité)

```python
from fastapi import HTTPException, status

def create_meeting(
    db: Session,
    meeting_in: MeetingCreate,
    current_user: User
) -> Meeting:
    """Créer une réunion avec validation de sécurité."""

    # 1. Service = celui de l'utilisateur (automatique)
    service_id = current_user.service_id

    # 2. Validation des projets (SÉCURITÉ CRITIQUE)
    user_project_ids = {p.id for p in current_user.projects}
    
    for project_id in meeting_in.project_ids or []:
        if project_id not in user_project_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Vous ne pouvez pas taguer le projet {project_id} : vous n'en êtes pas membre."
            )

    # 3. Création
    new_meeting = Meeting(
        title=meeting_in.title,
        service_id=service_id,
        owner_id=current_user.id,
        is_confidential=meeting_in.is_confidential or False,
    )

    # 4. Ajout des projets validés
    if meeting_in.project_ids:
        projects = db.query(Project).filter(Project.id.in_(meeting_in.project_ids)).all()
        new_meeting.projects = projects

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting
```

---

## 🗺️ Roadmap d'Implémentation

### 🏗️ Étape 1 : Le Modèle de Données (Backend)

**Fichiers :** `03-interface/backend/app/models/`

- [ ] Créer `models/organization.py` (Service, Project, tables d'association)
- [ ] Modifier `models/user.py` (ajouter `service_id`, relation `projects`)
- [ ] Modifier `models/meeting.py` (ajouter `service_id`, `is_confidential`, `owner_id`, `projects`)

---

### 🌱 Étape 2 : Le Script de Seed

**Fichier :** `03-interface/backend/app/db/init_db.py`

- [ ] Créer les Services par défaut (R&D, Sales, Marketing)
- [ ] Créer les Projets par défaut (Lancement V5, Audit Sécurité)
- [ ] Assigner le SuperUser au service R&D + tous les projets

---

### 🔌 Étape 3 : L'API

**Fichiers :** `03-interface/backend/app/`

- [ ] Mettre à jour `schemas/user.py` (UserRead avec `service`, `projects`)
- [ ] Créer `api/v1/endpoints/organization.py` (GET /services/, GET /projects/)
- [ ] Sécuriser `api/v1/endpoints/meetings.py` (validation tagging)

---

### 🎨 Étape 4 : Le Frontend (Next.js)

- [ ] Connecter `/login` avec le backend
- [ ] Créer le User Context (stocker `service`, `projects`)
- [ ] Rendre la Sidebar dynamique (afficher les projets de l'utilisateur)

---

## ✅ Critères de Succès

```bash
# 1. Lancer l'application
./manage.sh

# 2. Vérifier la DB
# → Services : R&D, Sales, Marketing
# → Projets : Lancement V5, Audit Sécurité

# 3. Se connecter
# → La Sidebar affiche les projets de l'utilisateur

# 4. Uploader un fichier
# → service_id = auto (celui de l'utilisateur)
# → Validation 403 si tagging projet non autorisé
```

---

## 📚 Ressources

- [SQLAlchemy Many-to-Many](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [ON DELETE SET NULL](https://www.postgresql.org/docs/current/ddl-constraints.html)
