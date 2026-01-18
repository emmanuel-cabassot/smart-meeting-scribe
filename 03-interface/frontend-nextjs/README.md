# Smart Meeting Scribe - Frontend

Application web moderne construite avec Next.js 16 pour la gestion et la transcription de réunions.

## 🛠 Technologies

| Catégorie | Technologie |
|---|---|
| **Framework** | Next.js 16 (App Router) + React 19 |
| **Langage** | TypeScript |
| **State** | Zustand (avec persistance localStorage) |
| **Styles** | Tailwind CSS v4 |
| **UI** | Radix UI, Lucide Icons, shadcn/ui pattern |
| **Build** | Turbopack |

## 📂 Architecture du Projet

```
src/
├── app/                    # Routing (App Router)
│   ├── (auth)/            # Routes publiques (login, register)
│   ├── (dashboard)/       # Routes protégées
│   │   ├── page.tsx       # Dashboard principal
│   │   ├── upload/        # Page upload
│   │   ├── meetings/[id]/ # Détail meeting
│   │   └── settings/      # Paramètres
│   ├── layout.tsx         # Layout racine
│   └── globals.css        # Design system (CSS variables)
│
├── components/
│   ├── ui/                # Composants atomiques (Button, Input, Badge...)
│   ├── layout/            # Structure (Sidebar, Header, MainLayout)
│   ├── meeting/           # Composants meeting détail
│   │   ├── MeetingDetail.tsx
│   │   ├── MeetingHeader.tsx
│   │   ├── MeetingToolbar.tsx
│   │   ├── TranscriptView.tsx
│   │   └── transcript-utils.ts
│   ├── features/          # Composants métier (SmartCard, VideoUpload)
│   └── common/            # Utilitaires (Spinner, StatusBadge)
│
├── hooks/
│   ├── use-auth.ts        # Authentification
│   ├── use-upload.ts      # Upload avec progress XHR
│   ├── use-polling.ts     # Polling status transcription
│   └── use-transcript.ts  # Fetch transcription
│
├── lib/
│   ├── api.ts             # Wrapper fetch type-safe + intercepteur 401
│   └── utils.ts           # cn(), formatDate(), formatDuration()
│
├── stores/
│   └── auth-store.ts      # Zustand (token, user, persistance)
│
└── types/
    ├── user.ts
    ├── meeting.ts
    └── group.ts
```

## ✨ Fonctionnalités Implémentées

### Authentification
- [x] Login / Register avec JWT
- [x] Persistance token + user dans localStorage
- [x] Redirection auto sur 401

### Layout & Navigation
- [x] Sidebar avec groupes
- [x] Header avec recherche + user dropdown
- [x] Breadcrumb
- [x] Dark theme complet

### Upload
- [x] Drag & Drop zone
- [x] Progress bar temps réel (XHR)
- [x] Sélection groupes multi-select
- [x] Validation type fichier + taille max 2GB

### Dashboard
- [x] Liste meetings avec polling status
- [x] Empty state

### Page Détail Meeting
- [x] Vue Groupée (fusionne segments consécutifs)
- [x] Vue Détaillée (timestamps)
- [x] Recherche insensible accents/casse
- [x] Statistiques speakers (temps de parole)
- [x] Export presse-papier / `.txt`
- [x] Couleurs distinctes par speaker

### 🚧 En cours (Phase 1 MVP)
- [ ] Middleware routes protégées
- [ ] MediaPlayer (audio/video)
- [ ] CRUD meetings (edit title, delete)
- [ ] Page settings

## 🚀 Démarrage

### Pré-requis
- Node.js 20+
- Backend Python accessible (`http://localhost:5000`)

### Installation

```bash
npm install
```

### Développement

```bash
npm run dev
```

→ [http://localhost:3000](http://localhost:3000)

### Build Production

```bash
npm run build && npm start
```

## 🐳 Docker

```bash
# Tous les services
docker compose up -d

# Rebuild frontend uniquement
./manage.sh rebuild frontend
```

## 📝 Roadmap

Voir [`FRONTEND_PHASE1_MVP.md`](../../FRONTEND_PHASE1_MVP.md) pour le suivi détaillé de la Phase 1.

---

*Dernière mise à jour : 18 Janvier 2026*
