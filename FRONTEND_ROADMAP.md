# 🎨 Frontend Roadmap - Smart Meeting Scribe V6.0

> Guide complet pour la création du frontend Next.js 16 - Style Modern Dark (Linear.app / YouTube Studio)

---

## 🎯 Vision Produit

Smart Meeting Scribe V6.0 est une **plateforme intelligente d'analyse de réunions** qui combine transcription automatique, identification des speakers, et intelligence artificielle pour extraire des insights actionnables.

### Fonctionnalités Clés
- 📹 **Support Audio & Vidéo** - Upload et traitement de fichiers audio/vidéo
- 🎤 **Transcription automatique** - Whisper Large-v3-Turbo avec identification des speakers
- 🏢 **Groupes** - Organisation par Départements, Projets, Réunions Récurrentes
- 💬 **RAG Chat** (Future) - Interroger vos réunions avec un LLM
- 📊 **Smart Insights** - Résumés automatiques et actions extraites

---

## 📋 État Actuel

### ✅ Backend API Disponible
- Authentification JWT (login/register)
- Upload audio/vidéo avec sélection de groupes
- Pipeline IA : Diarisation → Identification → Transcription
- CRUD Meetings avec filtres (groupe, status)
- CRUD Groups
- Webhook pour status updates

### ❌ Frontend à Créer
- Toutes les pages UI
- Design system moderne
- Composants réutilisables
- State management
- Upload avec drag & drop
- Lecteur audio/vidéo intégré
- Chat RAG interface

---

## 🎨 Design System - "Linear Dark"

### Philosophie
- **Dark-first** : Fond très sombre (presque noir)
- **Glassmorphism** : Effets de transparence subtils
- **Data-rich** : L'interface expose beaucoup d'informations de manière élégante
- **Micro-interactions** : Animations fluides et feedback immédiat

### Palette de Couleurs
```css
/* Backgrounds */
--bg-primary: #0A0A0B;        /* Presque noir */
--bg-secondary: #141416;      /* Sidebar, cards */
--bg-tertiary: #1C1C1F;       /* Headers, hover states */
--bg-glass: rgba(255, 255, 255, 0.05); /* Glassmorphism */

/* Accents */
--accent-primary: #8B5CF6;    /* Violet/Indigo */
--accent-secondary: #6366F1;  /* Indigo */
--accent-success: #10B981;    /* Vert */
--accent-warning: #F59E0B;    /* Orange */
--accent-error: #EF4444;      /* Rouge */

/* Text */
--text-primary: #FAFAFA;      /* Blanc cassé */
--text-secondary: #A1A1AA;    /* Gris clair */
--text-tertiary: #71717A;     /* Gris moyen */

/* Borders */
--border-subtle: rgba(255, 255, 255, 0.08);
--border-bright: rgba(255, 255, 255, 0.12);

/* Status Colors */
--status-pending: #F59E0B;    /* Orange */
--status-processing: #3B82F6; /* Bleu */
--status-completed: #10B981;  /* Vert */
--status-failed: #EF4444;     /* Rouge */
```

### Typographie
- **Police principale** : `Inter` (Google Fonts)
- **Police mono** : `JetBrains Mono` (transcriptions, code)
- **Tailles** :
  - H1: 2rem (32px) - Bold
  - H2: 1.5rem (24px) - Semibold
  - Body: 0.875rem (14px) - Regular
  - Small: 0.75rem (12px) - Regular

### Effets & Styles
```css
/* Glassmorphism Card */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

/* Subtle Shadow */
.card-shadow {
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
}

/* Hover Glow */
.hover-glow:hover {
  box-shadow: 0 0 24px rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
}
```

---

## 🏗️ Architecture des Pages

### Layout Principal (3 zones)

```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  🔍 Search...           [👤 EC ▼] [📤 Upload] │  ← Top Header
├──────────┬──────────────────────────────────────────────┤
│          │  Home > My Feed                              │
│  📊 MY   │                                              │
│  GROUPS  │  ┌──────────────────────────────────┐       │
│          │  │ 🎯 Point Hebdo R&D               │       │
│  Depts   │  │ [V5] [Tech] • 2h ago             │       │
│  ├ R&D   │  │                                  │       │
│  ├ Sales │  │ ✨ AI Summary                    │       │  ← Main Content
│  └ HR    │  │ • Architecture S3 validée        │       │  (Smart Cards)
│          │  │ • ⚠️ Bloqueur Dockerfile GPU     │       │
│  Projects│  │ • Action: Patch avant midi       │       │
│  ├ V5    │  │                                  │       │
│  └ Audit │  │ [▶] ━━━●━━━━━━━ 45:23           │       │
│          │  └──────────────────────────────────┘       │
│  📅 Rec. │                                              │
│  ├ COMOP │  ┌──────────────────────────────────┐       │
│  └ Daily │  │ ... (autre card)                 │       │
│          │  └──────────────────────────────────┘       │
└──────────┴──────────────────────────────────────────────┘
  Sidebar      Main Feed
```

### Pages Détaillées

#### 1. `/login` - Authentification
- **Style** : Centré, glassmorphism card sur fond noir
- **Éléments** :
  - Logo + "Smart Scribe V6.0"
  - Input email (avec icône)
  - Input password (avec toggle visibility)
  - Button "Sign In" (violet, large)
  - Link "Create account" (subtil)

#### 1b. `/register` - Inscription
- **Style** : Identique à login
- **Éléments** :
  - Input email
  - Input password
  - Input confirm password
  - Button "Create Account"
  - Link "Already have an account?" → `/login`
- **Après inscription** : Redirect vers `/login` avec toast succès

> [!NOTE]
> Pas de confirmation email pour le MVP. À évaluer plus tard si nécessaire.

#### 2. `/` (Dashboard) - My Feed
**Top Header** :
- Breadcrumb : "Home > My Feed"
- Search bar (style Command Palette) : `⌘K` hint
- **User Dropdown** [👤 EC ▼] : Avatar + initiales, au clic :
  - Nom complet + email
  - ⚙️ Settings
  - 🚪 Logout
- Bouton "UPLOAD MEETING" (violet vif, call-to-action)

**Sidebar** (Navigation fixe) :

> [!NOTE]
> Les catégories `Departments`, `Projects`, `Recurring` correspondent à l'enum `GroupType`.
> Au démarrage, seul le groupe **"Tous"** (type `department`) existe par défaut (seed data).
> Les autres groupes (R&D, V5 Launch, COMOP...) sont **créés par l'utilisateur** via l'interface.

```
MY WORKSPACE
  📊 My Feed        ← Active
  📤 Uploads
  ⭐ Favorites

GROUPS                             ← Basé sur GroupType enum
  Departments                      ← GroupType.DEPARTMENT
    └─ 📁 Tous                     ← Groupe par défaut (seed)
    (+ groupes créés par l'utilisateur: R&D, Marketing...)
  
  Projects                         ← GroupType.PROJECT
    (vide au départ, créés par l'utilisateur)
  
  Recurring                        ← GroupType.RECURRING
    (vide au départ, créés par l'utilisateur)

PROFILE
  👤 Emmanuel C.
  ⚙️ Settings
```

**Main Content** :
- Titre "Recent Insights"
- Filtres rapides (Status: All, Pending, Completed)
- **Smart Cards Feed** (scrollable)

#### 3. Smart Card - Anatomie

```
┌─────────────────────────────────────────────────┐
│ 🗣️ Point Hebdo R&D                              │ ← Titre
│ [V5] [Tech] [Department: R&D]  • Il y a 2h     │ ← Badges + Date
├─────────────────────────────────────────────────┤
│                                                 │
│  ✨ AI Summary (encart violet translucide)     │ ← AI Insights
│  ✅ Architecture S3 validée                     │
│  ⚠️ Bloqueur sur le Dockerfile GPU             │
│  💡 Action: Emmanuel doit patcher avant midi   │
│                                                 │
├─────────────────────────────────────────────────┤
│ [▶] ━━━━●━━━━━━━━━━ 45:23 / 52:10             │ ← Audio/Video Player
│                                                 │
│ [📄 Read Transcript]  [💬 Chat]  [⋯ More]     │ ← Actions
└─────────────────────────────────────────────────┘
```

**États de la card** :
- `pending` : Spinner + "Transcribing..."
- `processing` : Progress bar (%)
- `completed` : AI Summary visible
- `failed` : Badge rouge + bouton "Retry"

**Menu [⋯ More]** (Dropdown) :
- ✏️ **Edit title** → Ouvre modal d'édition titre
- 📥 **Download** → Télécharger (JSON, TXT)
- 🗑️ **Delete** → Modal de confirmation, puis suppression

```
┌───────────────────────────┐
│ Edit title       ✏️      │
│ Download         📥      │
├───────────────────────────┤
│ Delete           🗑️      │  ← Rouge/danger
└───────────────────────────┘
```

#### 4. `/meetings/{id}` - Détail Transcription

**Layout** :
```
┌─────────────────────────────────────────────────┐
│ ← Back    Point Hebdo R&D          [⋯ Actions] │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 Metadata                                    │
│  • Created: 17 Jan 2026, 14:30                 │
│  • Duration: 52:10                              │
│  • Groups: [V5] [R&D]                          │
│  • Speakers: 3 (Emmanuel, Marie, Thomas)       │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ✨ AI Summary                                  │
│  (Encart glassmorphism avec insights)          │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  📝 Transcript (Timeline View)                 │
│                                                 │
│  [00:00] 👤 Emmanuel                           │
│  "Alors, on fait le point sur l'archi S3..."   │
│                                                 │
│  [01:23] 👤 Marie                              │
│  "Oui, j'ai terminé la migration boto3..."     │
│                                                 │
│  [02:45] 👤 Thomas                             │
│  "Par contre, j'ai un bloqueur GPU..."         │
│                                                 │
│  (scrollable)                                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Sidebar Droite (optionnelle)** :
- Jump to timestamp
- Search in transcript
- Speakers list
- Download options (JSON, TXT, PDF)

#### 5. `/upload` - Upload Audio/Vidéo

**Layout** :
```
┌─────────────────────────────────────────────────┐
│  Upload New Meeting                             │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │                                         │   │
│  │    📤  Drag & drop audio/video here    │   │
│  │         or click to browse              │   │
│  │                                         │   │
│  │    Supported: MP3, WAV, MP4, M4A       │   │
│  │    Max size: 2GB                        │   │
│  │                                         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  📝 Title (optional)                           │
│  [____________________________________]         │
│                                                 │
│  🏢 Select Groups (required)                   │
│  [x] R&D                                       │
│  [x] V5 Launch                                 │
│  [ ] Marketing                                 │
│  [ ] COMOP                                     │
│                                                 │
│  [Cancel]              [Upload & Process] →    │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### 6. `/settings` - Paramètres (MVP simple)

> [!NOTE]
> **MVP** : Page minimaliste. Les fonctionnalités avancées (groupes, intégrations) viendront en Phase 2.

- **Profil** : Afficher nom + email (read-only pour MVP)
- **Future** : Azure AD / Microsoft 365 integration (Teams, Outlook friendly)

> [!TIP]
> **Admin Features (Phase 2+)** : La gestion des groupes (CRUD), la gestion des utilisateurs, et les paramètres avancés seront dans une section Admin dédiée.

#### 7. `/chat` - RAG Chat (Phase 3) 🚀

**Concept** : Interroger vos réunions avec un LLM

**Layout** :
```
┌─────────────────────────────────────────────────┐
│  💬 Ask about your meetings                     │
├─────────────────────────────────────────────────┤
│  🎯 Context                                     │
│  [x] Point Hebdo R&D (17 Jan)                  │
│  [x] COMOP (15 Jan)                            │
│  [ ] All R&D meetings (Last 30 days)           │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  💬 Conversation                                │
│                                                 │
│  You: "Quels étaient les bloqueurs techniques  │
│        mentionnés cette semaine ?"              │
│                                                 │
│  AI: "D'après les réunions sélectionnées,      │
│       voici les bloqueurs identifiés:          │
│       1. Dockerfile GPU (Point Hebdo R&D)      │
│       2. Config Redis (COMOP)..."              │
│                                                 │
│  [Type your question...]                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Fonctionnalités RAG** :
- Sélection de meetings (individuel, par groupe, date range)
- Historique de conversation
- Citations avec lien vers timestamp
- Export de la conversation

---

## 📁 Architecture Frontend

### Arborescence du Projet

```
03-interface/frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/                   # Routes publiques (non connecté)
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── layout.tsx            # Layout auth (centré, sans sidebar)
│   │   │
│   │   ├── (dashboard)/              # Routes protégées (connecté)
│   │   │   ├── layout.tsx            # Layout avec Sidebar + TopHeader
│   │   │   ├── page.tsx              # Dashboard / My Feed
│   │   │   ├── meetings/
│   │   │   │   └── [id]/page.tsx     # Détail transcription
│   │   │   ├── upload/page.tsx       # Upload audio/vidéo
│   │   │   ├── chat/page.tsx         # RAG Chat (Phase 3)
│   │   │   └── settings/page.tsx     # Paramètres utilisateur
│   │   │
│   │   ├── layout.tsx                # Root layout (providers, fonts)
│   │   └── globals.css               # Styles globaux + design tokens
│   │
│   ├── components/                   # Composants React (Pattern Hybride)
│   │   ├── ui/                       # shadcn/ui (ne pas modifier)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── progress.tsx
│   │   │   └── ...
│   │   │
│   │   ├── common/                   # Composants réutilisables custom
│   │   │   ├── StatusBadge.tsx       # Badge status meeting (pending, completed...)
│   │   │   ├── GroupBadge.tsx        # Badge type groupe (dept, project, recurring)
│   │   │   ├── MediaPlayer.tsx       # Wrapper simple HTML5 audio/video
│   │   │   └── LoadingSpinner.tsx    # Spinner de chargement
│   │   │
│   │   ├── layout/                   # Structure de l'application
│   │   │   ├── Sidebar.tsx           # Navigation latérale (groupes, menu)
│   │   │   ├── TopHeader.tsx         # Header (search, upload, user dropdown)
│   │   │   ├── UserDropdown.tsx      # Menu utilisateur (settings, logout)
│   │   │   ├── MainLayout.tsx        # Wrapper 3 zones
│   │   │   └── Breadcrumb.tsx        # Navigation fil d'ariane
│   │   │
│   │   └── features/                 # Composants par domaine métier
│   │       ├── meetings/
│   │       │   ├── SmartCard.tsx     # Card meeting dans le feed
│   │       │   ├── TranscriptView.tsx # Vue timeline transcription
│   │       │   ├── AIInsights.tsx    # Encart résumé IA
│   │       │   └── MeetingFilters.tsx # Filtres (status, groupe, date)
│   │       │
│   │       ├── upload/
│   │       │   ├── FileDropzone.tsx  # Zone drag & drop
│   │       │   ├── GroupSelector.tsx # Multi-select groupes
│   │       │   └── UploadProgress.tsx # Barre de progression
│   │       │
│   │       ├── chat/                 # (Phase 3)
│   │       │   ├── ChatInterface.tsx # Interface conversationnelle
│   │       │   ├── ContextSelector.tsx # Sélection meetings/groupes
│   │       │   └── MessageBubble.tsx # Bulle message AI/User
│   │       │
│   │       └── groups/
│   │           ├── GroupList.tsx     # Liste des groupes sidebar
│   │           └── GroupForm.tsx     # Création/édition groupe
│   │
│   ├── lib/                          # Utilitaires et configuration
│   │   ├── api.ts                    # Wrapper fetch + interceptors
│   │   ├── utils.ts                  # cn(), formatDate(), formatDuration()
│   │   └── validations.ts            # Schémas Zod (forms)
│   │
│   ├── hooks/                        # React hooks custom
│   │   ├── use-auth.ts               # Auth state + actions
│   │   ├── use-meetings.ts           # React Query meetings
│   │   ├── use-groups.ts             # React Query groups
│   │   └── use-upload.ts             # Upload mutation
│   │
│   ├── stores/                       # Zustand global state
│   │   └── auth-store.ts             # Token, user, isAuthenticated
│   │
│   └── types/                        # Types TypeScript
│       ├── meeting.ts                # Meeting, MeetingStatus
│       ├── group.ts                  # Group, GroupType
│       └── user.ts                   # User
│
├── public/                           # Assets statiques
│   ├── logo.svg
│   └── favicon.ico
│
├── tailwind.config.ts                # Config Tailwind + design tokens
├── components.json                   # Config shadcn/ui
├── next.config.ts                    # Config Next.js
├── tsconfig.json                     # Config TypeScript
└── package.json
```

### Pattern d'Organisation (Hybride)

| Dossier | Contenu | Règle |
|---------|---------|-------|
| `ui/` | Composants shadcn/ui | ❌ Ne pas modifier directement |
| `common/` | Composants réutilisables custom | ✅ Utilisé sur 2+ pages |
| `layout/` | Structure app (Sidebar, Header) | ✅ Toujours visible |
| `features/` | Composants métier par domaine | ✅ Spécifique à un domaine |

> [!TIP]
> **Règle simple** : Si un composant est utilisé sur plusieurs pages → `common/`. Sinon → `features/{domain}/`

---

## 🎯 Stratégie UX

### Philosophie : Simple d'abord, extensible ensuite

L'architecture permet d'ajouter des features sans refactoring majeur. Le MVP reste épuré.

### Affichage des Meetings

| Feature | MVP (Phase 1) | Future (Phase 2+) |
|---------|---------------|-------------------|
| **Mode d'affichage** | SmartCards uniquement | + Mode Compact (grid) |
| **Sections temporelles** | "Cette semaine" / "Plus ancien" | Groupement avancé par mois |
| **Infinite scroll** | ✅ Oui | ✅ Oui |
| **Multi-select** | ❌ Non | ✅ Checkbox + "Chat with selected" |

**MVP** : Cards full-width avec preview AI, groupées simplement.
```
┌────────────────────────────────────────────────────────────┐
│ 📅 Cette semaine                                           │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🎯 Point Hebdo R&D              Il y a 2h • 52min  │   │
│  │ ✨ "Architecture S3 validée, bloqueur GPU..."      │   │
│  │ [▶ Écouter]  [📄 Transcript]  [💬 Chat]           │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│ 📅 Plus ancien                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ ...                                                │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### Search & RAG

| Feature | MVP (Phase 1) | Future (Phase 2+) |
|---------|---------------|-------------------|
| **Search bar** | Recherche par titre | + RAG AI intégré |
| **Accès Chat** | Bouton sur chaque meeting | + "Chat all [Group]" sidebar |
| **Command Palette** | ❌ Non | ⌘K avec suggestions AI |

**MVP** : Search simple par titre. Le RAG est accessible via le bouton "Chat" sur chaque meeting individuel.

**Future** : La search bar devient RAG-first avec résultats mixtes (meetings + réponse AI).

### Sidebar & Groupes

| Feature | MVP (Phase 1) | Future (Phase 2+) |
|---------|---------------|-------------------|
| **Structure** | 3 catégories fixes (Dept, Project, Recurring) | Collapsible + recherche |
| **Groupe "Tous"** | ✅ Par défaut (seed) | ✅ |
| **Raccourci Chat** | ❌ Non | Bouton "Chat all" par groupe |
| **Compteur meetings** | ✅ Badge (12) | ✅ |

### Extensibilité Technique

L'architecture composants permet d'ajouter :

```typescript
// MVP: Un seul mode
<MeetingList meetings={meetings} />

// Future: Props pour le mode
<MeetingList 
  meetings={meetings} 
  viewMode="cards" | "compact" | "timeline"  // Ajouté plus tard
  selectable={true}                          // Ajouté plus tard
  onSelectionChange={handleSelection}        // Ajouté plus tard
/>
```

> [!IMPORTANT]
> **Règle d'or** : Implémenter le minimum, mais concevoir les interfaces (props, types) pour l'extensibilité.

---

## 🔄 États UI & Comportements

### Loading States

| Contexte | Composant | Comportement |
|----------|-----------|--------------|
| **Page initiale** | Skeleton | Cards placeholder animées |
| **Refresh données** | Spinner discret | En haut à droite, non bloquant |
| **Upload fichier** | ProgressBar | Pourcentage + nom fichier |
| **Action bouton** | Button disabled + spinner | "Uploading..." / "Saving..." |

```typescript
// Pattern Loading
{isLoading ? (
  <MeetingCardSkeleton count={3} />
) : (
  <MeetingList meetings={meetings} />
)}
```

### Error States

| Type d'erreur | Code | Comportement |
|---------------|------|--------------|
| **Non authentifié** | 401 | Redirect `/login` + toast "Session expirée" |
| **Non autorisé** | 403 | Toast "Accès refusé" |
| **Not found** | 404 | Page 404 avec bouton retour |
| **Erreur serveur** | 500 | Toast "Erreur serveur" + bouton Retry |
| **Network error** | - | Toast "Connexion perdue" + retry auto |
| **Upload échoué** | - | Toast + bouton "Réessayer" |

```typescript
// Pattern Error Handling (intégré dans lib/api.ts)
// Le wrapper fetch gère déjà le 401 automatiquement

// Pour les erreurs 500+, utiliser un hook ou composant wrapper :
const useFetchWithToast = <T>(queryKey: string[], fn: () => Promise<T>) => {
  return useQuery({
    queryKey,
    queryFn: fn,
    onError: (error: ApiError) => {
      if (error.status >= 500) {
        toast.error('Erreur serveur. Réessayez.');
      } else if (error.status === 403) {
        toast.error('Accès refusé');
      }
    },
  });
};
```

### Empty States

| Contexte | Message | Action |
|----------|---------|--------|
| **Dashboard (0 meetings)** | "Aucune réunion pour le moment" | Bouton "Upload your first meeting" |
| **Groupe vide** | "Aucune réunion dans ce groupe" | Bouton "Upload" |
| **Search sans résultat** | "Aucun résultat pour 'xxx'" | Suggestions ou "Effacer la recherche" |
| **Filtres sans résultat** | "Aucune réunion avec ces filtres" | Bouton "Réinitialiser les filtres" |

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│              📭 Aucune réunion pour le moment              │
│                                                            │
│     Uploadez votre premier fichier audio ou vidéo         │
│     pour commencer à transcrire vos réunions.              │
│                                                            │
│              [📤 Upload your first meeting]                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Validation Formulaires

| Champ | Règles | Message d'erreur |
|-------|--------|------------------|
| **Email** | Format email valide | "Email invalide" |
| **Password** | Min 8 caractères | "8 caractères minimum" |
| **Titre meeting** | Max 255 caractères | "Titre trop long" |
| **Fichier** | Max 2GB, formats audio/video | "Fichier trop volumineux (max 2GB)" |
| **Groupes** | Au moins 1 sélectionné | "Sélectionnez au moins un groupe" |

```typescript
// Zod Schema exemple
const uploadSchema = z.object({
  file: z.instanceof(File)
    .refine(f => f.size <= 2 * 1024 * 1024 * 1024, 'Max 2GB')
    .refine(f => ALLOWED_TYPES.includes(f.type), 'Format non supporté'),
  title: z.string().max(255).optional(),
  groupIds: z.array(z.number()).min(1, 'Sélectionnez au moins un groupe'),
});
```

### Real-time Status Updates

**Stratégie : Polling** (pas de WebSocket pour simplifier le MVP)

| Status | Intervalle polling | Action |
|--------|-------------------|--------|
| `pending` | 5 secondes | Continuer polling |
| `processing` | 3 secondes | Afficher progress si disponible |
| `completed` | Stop polling | Afficher résultat + toast succès |
| `failed` | Stop polling | Afficher erreur + bouton Retry |

```typescript
// Hook usePollingStatus
const useMeetingStatus = (meetingId: number) => {
  return useQuery({
    queryKey: ['meeting', meetingId],
    queryFn: () => api.get(`/meetings/${meetingId}`),
    refetchInterval: (data) => {
      const status = data?.status;
      if (status === 'pending') return 5000;
      if (status === 'processing') return 3000;
      return false; // Stop polling
    },
  });
};
```

### Toasts & Notifications

| Événement | Type | Message | Durée |
|-----------|------|---------|-------|
| Upload démarré | info | "Upload en cours..." | 3s |
| Upload terminé | success | "Fichier uploadé. Transcription en cours..." | 5s |
| Transcription terminée | success | "Transcription terminée !" | 5s + lien |
| Erreur | error | Message d'erreur dynamique | 8s |
| Session expirée | warning | "Session expirée. Reconnectez-vous." | 10s |

---

## 🔌 Contrat API

> [!IMPORTANT]
> **Source de vérité** : Voir [`03-interface/backend/README.md`](./03-interface/backend/README.md) pour la documentation API complète.
> Les routes ci-dessous sont un résumé pour le frontend.

### Authentication (`/api/v1/auth`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/register` | ❌ | Créer un compte |
| `POST` | `/login` | ❌ | Obtenir un JWT (form-data: username, password) |

```typescript
// Login
POST /api/v1/auth/login
Body (form-data): { username: string, password: string }
Response: { access_token: string, token_type: "bearer" }

// Register
POST /api/v1/auth/register
Body: { email: string, password: string, full_name?: string }
Response: UserOut
```

### Users (`/api/v1/users`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/me` | ✅ | Profil utilisateur avec ses groupes |

```typescript
GET /api/v1/users/me
Headers: Authorization: Bearer {token}
Response: {
  id: number,
  email: string,
  full_name: string,
  groups: Array<{ id: number, name: string, type: GroupType }>
}
```

### Process/Upload (`/api/v1/process`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/` | ✅ | Upload audio → créer Meeting → dispatch Worker |
| `GET` | `/status/{task_id}` | ❌ | Polling du statut de transcription |

```typescript
POST /api/v1/process/
Headers: Authorization: Bearer {token}
Body (multipart/form-data):
  - file: File (audio/video)
  - title?: string
  - group_ids: string  // JSON array "[1, 2]"

Response: {
  status: string,
  meeting_id: string,
  task_id: string,
  s3_path: string,
  message: string
}

GET /api/v1/process/status/{task_id}
Response: { status: string, progress?: number, result?: TranscriptionResult }
```

### Meetings (`/api/v1/meetings`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/` | ✅ | Liste meetings (visibles selon groupes) |
| `GET` | `/?group_id=1` | ✅ | Filtre par groupe |
| `GET` | `/?status=pending` | ✅ | Filtre par status |
| `GET` | `/mine` | ✅ | Liste mes meetings uniquement |
| `GET` | `/{id}` | ✅ | Détail d'un meeting |
| `PATCH` | `/{id}` | ✅ Owner | Modifier un meeting (title, etc.) |
| `DELETE` | `/{id}` | ✅ Owner | Supprimer un meeting |
| `GET` | `/stats/count` | ✅ | Compteur de meetings |

```typescript
GET /api/v1/meetings/
Query: { group_id?: number, status?: string }
Response: Array<MeetingOut>

GET /api/v1/meetings/{id}
Response: MeetingOut

PATCH /api/v1/meetings/{id}
Body: { title?: string }
Response: MeetingOut

DELETE /api/v1/meetings/{id}
Response: 204 No Content
```

### Groups (`/api/v1/groups`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/` | ✅ | Liste tous les groupes |
| `GET` | `/{id}` | ✅ | Détail d'un groupe |
| `POST` | `/` | 🔐 Admin | Créer un groupe |
| `PATCH` | `/{id}` | 🔐 Admin | Modifier un groupe |
| `DELETE` | `/{id}` | 🔐 Admin | Supprimer un groupe |

```typescript
GET /api/v1/groups/
Response: Array<{
  id: number,
  name: string,
  description: string,
  type: "department" | "project" | "recurring",
  is_active: boolean
}>
```

### Future: RAG Chat (Phase 3)
```typescript
POST /api/v1/chat/query
Body: {
  query: string,
  meeting_ids?: number[],
  group_ids?: number[],
  date_range?: { start: string, end: string }
}
Response: {
  answer: string,
  sources: Array<{ meeting_id: number, timestamp: number, text: string }>
}
```

---

## 🚀 Roadmap par Phases

### Phase 1 - MVP Core (2-3 semaines)
**Objectif** : App fonctionnelle avec upload et visualisation

- [x] Setup Next.js 16 + TypeScript + TailwindCSS
- [ ] Design system (composants UI de base)
- [ ] Auth (Login/Register)
- [ ] Sidebar navigation + Top Header
- [ ] Dashboard (Smart Cards feed)
- [ ] Upload audio/vidéo avec groupe selector
- [ ] Page détail transcription (simple)
- [ ] Status polling (pending → completed)

**Critères de succès** :
- ✅ Je peux me connecter
- ✅ Je peux uploader un fichier
- ✅ Je vois le statut de traitement
- ✅ Je peux lire la transcription finale

### Phase 2 - Enhanced UX (2 semaines)
**Objectif** : Expérience utilisateur premium

- [ ] Lecteur audio/vidéo intégré dans les cards
- [ ] Filtres avancés (groupe, date, status)
- [ ] Search globale (Command Palette style)
- [ ] Gestion d'erreurs + Retry
- [ ] AI Summary basique (parsing JSON transcription)
- [ ] Download transcript (TXT, JSON)
- [ ] Real-time updates (WebSocket ou polling)
- [ ] Animations & micro-interactions

**Critères de succès** :
- ✅ L'interface est fluide et réactive
- ✅ Je peux écouter l'audio sans quitter la page
- ✅ Je vois un résumé structuré au lieu d'un dump JSON

### Phase 3 - Intelligence & RAG (3-4 semaines)
**Objectif** : Assistant IA conversationnel

- [ ] Backend RAG (Qdrant + LLM)
- [ ] Page `/chat` - Interface conversationnelle
- [ ] Sélection de contexte (meetings, groupes, dates)
- [ ] Citations avec liens vers timestamps
- [ ] Génération de vrais AI Insights (actions, décisions, bloqueurs)
- [ ] Export conversations
- [ ] Notifications intelligentes

**Critères de succès** :
- ✅ Je peux poser des questions sur mes réunions
- ✅ L'IA cite les sources avec timestamps
- ✅ Les Smart Cards affichent de vrais insights actionnables

### Phase 4 - Polish & Scale (2 semaines)
**Objectif** : Production-ready

- [ ] Tests E2E (Playwright)
- [ ] Optimisations performance
- [ ] SEO & metadata
- [ ] Responsive mobile
- [ ] Dark/Light mode toggle (optionnel)
- [ ] User preferences & settings
- [ ] Analytics dashboard
- [ ] Export PDF/Word

---

## 🛠️ Stack Technique

| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **Next.js 16** | Framework (App Router) | SSR, routing, optimisations |
| **TypeScript** | Type safety | Meilleure DX, moins de bugs |
| **TailwindCSS** | Styling | Rapide, moderne, customizable |
| **shadcn/ui** | Composants UI | Composants accessibles, customizables, copy-paste |
| **Framer Motion** | Animations | Micro-interactions fluides |
| **React Query** | Data fetching | Cache, invalidation, refetch |
| **Zustand** | Global state | Simple, performant |
| **React Hook Form** | Formulaires | Validation, performance |
| **Zod** | Validation schemas | Type-safe schemas |
| **Lucide Icons** | Icônes | SVG, tree-shakeable (inclus avec shadcn/ui) |

> [!TIP]
> **Audio/Vidéo** : Pour le MVP, on utilise les players HTML5 natifs (`<audio controls>` / `<video controls>`).
> Pas besoin de Howler.js ou Video.js. À ajouter en Phase 2 si besoin de features avancées (waveform, playback speed, etc.).

---

## 📝 Exemples de Code

### API Client avec Fetch (Wrapper)
```typescript
// lib/api.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function api<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token = typeof window !== 'undefined' 
    ? localStorage.getItem('token') 
    : null;

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });

  // Handle 401 globally
  if (res.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new ApiError(401, 'Session expirée');
  }

  if (!res.ok) {
    throw new ApiError(res.status, await res.text());
  }

  return res.json();
}

// Helpers
export const apiGet = <T>(url: string) => api<T>(url);
export const apiPost = <T>(url: string, body: unknown) =>
  api<T>(url, { method: 'POST', body: JSON.stringify(body) });
export const apiDelete = <T>(url: string) =>
  api<T>(url, { method: 'DELETE' });

export default api;
```

### Upload avec Progress (XMLHttpRequest)
```typescript
// lib/upload.ts
export function uploadWithProgress(
  file: File,
  groupIds: number[],
  title?: string,
  onProgress?: (percent: number) => void
): Promise<MeetingOut> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const token = localStorage.getItem('token');

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(xhr.responseText));
      }
    });

    xhr.addEventListener('error', () => reject(new Error('Upload failed')));

    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    formData.append('group_ids', JSON.stringify(groupIds));

    xhr.open('POST', `${BASE_URL}/api/v1/process/`);
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
}
```

### Hook Upload avec React Query
```typescript
// hooks/useUpload.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadWithProgress } from '@/lib/upload';

interface UploadParams {
  file: File;
  title?: string;
  groupIds: number[];
  onProgress?: (percent: number) => void;
}

export const useUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, title, groupIds, onProgress }: UploadParams) =>
      uploadWithProgress(file, groupIds, title, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] });
    },
  });
};
```

### Smart Card Component
```typescript
// components/Meeting/SmartCard.tsx
import { Badge } from '@/components/UI/Badge';
import { AudioPlayer } from '@/components/Meeting/AudioPlayer';
import { AIInsights } from '@/components/Meeting/AIInsights';

export const SmartCard = ({ meeting }) => {
  return (
    <div className="glass-card p-6 hover-glow transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-primary">
          {meeting.title}
        </h3>
        <span className="text-sm text-tertiary">
          {formatRelativeTime(meeting.created_at)}
        </span>
      </div>

      {/* Badges */}
      <div className="flex gap-2 mb-4">
        {meeting.groups.map((group) => (
          <Badge key={group.id} type={group.type}>
            {group.name}
          </Badge>
        ))}
        <Badge status={meeting.status} />
      </div>

      {/* AI Insights (si completed) */}
      {meeting.status === 'completed' && meeting.insights && (
        <AIInsights insights={meeting.insights} />
      )}

      {/* Audio Player */}
      {meeting.status === 'completed' && (
        <AudioPlayer src={meeting.audio_url} duration={meeting.duration} />
      )}

      {/* Actions */}
      <div className="flex gap-3 mt-4">
        <Button variant="secondary" href={`/meetings/${meeting.id}`}>
          📄 Read Transcript
        </Button>
        {meeting.insights && (
          <Button variant="ghost" href={`/chat?meeting=${meeting.id}`}>
            💬 Chat
          </Button>
        )}
      </div>
    </div>
  );
};
```

---

## 🧪 Testing Strategy

### Unit Tests (Jest + RTL)
- Composants UI (Button, Input, Card...)
- Hooks custom (useUpload, useMeetings...)
- Utils functions

### Integration Tests
- Flux complets (Login → Upload → View)
- API mocking avec MSW

### E2E Tests (Playwright)
- User journey critique :
  1. Login
  2. Upload meeting
  3. Wait for completion
  4. View transcript
  5. Ask question (RAG)

---

## 🚦 Definition of Done

Une feature est **Done** quand :
- ✅ Code fonctionnel et typé (TypeScript strict)
- ✅ Responsive (mobile + desktop + tablet)
- ✅ Gestion d'erreurs (network, 401, 500...)
- ✅ Loading states (spinners, skeletons)
- ✅ Accessible (a11y basics WCAG 2.1)
- ✅ Tests unitaires (coverage > 70%)
- ✅ Animations fluides (60fps)
- ✅ Documentation (README + JSDoc)

---

*Document créé le 17 Janvier 2026 - Version 2.0*
