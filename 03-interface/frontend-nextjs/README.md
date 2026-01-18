# Smart Meeting Scribe - Frontend

Application web moderne construite avec Next.js 15+ pour la gestion et la transcription de réunions.

## 🛠 Technologies

- **Framework** : [Next.js 16](https://nextjs.org/) (App Router)
- **Langage** : [TypeScript](https://www.typescriptlang.org/)
- **State Management** : [Zustand](https://github.com/pmndrs/zustand) (avec persistance)
- **UI Components** :
  - [Tailwind CSS v4](https://tailwindcss.com/)
  - [Radix UI](https://www.radix-ui.com/) (primitives accessibles)
  - [Lucide React](https://lucide.dev/) (icônes)
- **Data Fetching** : Fetch native avec wrapper type-safe
- **Forms** : Gestion native contrôlée + validation
- **Build Tool** : Turbopack (via Next.js)

## 📂 Architecture du Projet

Le projet suit l'architecture **Next.js App Router** avec une séparation claire des responsabilités.

```
src/
├── app/                    # Routing et Pages (App Router)
│   ├── (auth)/            # Routes d'authentification (login, register)
│   ├── (dashboard)/       # Routes protégées (upload, meetings)
│   ├── layout.tsx         # Layout racine (Providers, Font)
│   └── globals.css        # Styles globaux (Tailwind @theme)
│
├── components/            # Composants React
│   ├── ui/                # Composants atomiques réutilisables (Button, Input, Badge...)
│   ├── layout/            # Composants de structure (Header, Sidebar)
│   ├── meeting/           # Composants pour la page de détail meeting
│   │   ├── MeetingDetail.tsx      # Conteneur principal
│   │   ├── MeetingHeader.tsx      # En-tête avec titre, date, légende speakers
│   │   ├── MeetingToolbar.tsx     # Barre d'outils (recherche, vues, export)
│   │   ├── TranscriptView.tsx     # Affichage des segments (groupé/détaillé)
│   │   └── transcript-utils.ts    # Utilitaires (couleurs, formatage, recherche)
│   ├── features/          # Composants métier complexes
│   └── common/            # Composants utilitaires (Spinner, etc.)
│
├── hooks/                 # Custom Hooks
│   ├── use-auth.ts        # Hook d'authentification et gestion session
│   ├── use-transcript.ts  # Récupération des données de transcription
│   ├── use-upload.ts      # Logique d'upload
│   └── use-polling.ts     # Polling pour le statut des transcriptions
│
├── lib/                   # Utilitaires et Configuration
│   ├── api.ts             # Wrapper fetch, gestion erreurs, intercepteurs auth
│   └── utils.ts           # Fonctions helpers (cn, formatters)
│
├── stores/               # État Global (Zustand)
│   └── auth-store.ts      # Store d'auth (token, user data, persistance)
│
└── types/                # Définitions TypeScript
    ├── user.ts            # Interfaces User, Login, Register
    ├── meeting.ts         # Interfaces Meeting, Transcription
    └── group.ts           # Interfaces Groupes
```

## ✨ Fonctionnalités Clés

### Authentification
- Login / Register avec JWT.
- Persistance automatique du token et du profil user dans `localStorage`.
- Redirection automatique si non authentifié ou token expiré (401).

### Upload de Fichier
- Support du Drag & Drop.
- Upload avec barre de progression temps réel.
- Assignation obligatoire de groupes (département, projet...).

### Dashboard
- Liste des meetings avec statut en temps réel (polling).
- Vue détaillée des transcriptions interactives (diarisation).

### Page Détail Meeting (`/meetings/[id]`)
- **Vue Groupée par Speaker** : Fusionne les segments consécutifs d'un même intervenant.
- **Vue Détaillée** : Affiche chaque segment individuellement avec timestamps.
- **Recherche** : Filtrage en temps réel, insensible aux accents et à la casse.
- **Statistiques Speakers** : Popover affichant le temps de parole par intervenant.
- **Export** : Copier dans le presse-papier ou télécharger en `.txt`.
- **Couleurs distinctes** : Attribution déterministe de couleurs pour chaque speaker.

## 🚀 Démarrage

### Pré-requis
- Node.js 20+
- Backend Python lancé et accessible (par défaut `http://localhost:5000`)

### Installation

```bash
npm install
```

### Développement

Lancer le serveur de développement avec Turbopack (Hot Reload ultra-rapide) :

```bash
npm run dev
```

L'application sera accessible sur [http://localhost:3000](http://localhost:3000).

### Build Production

```bash
npm run build
npm start
```

## 🐳 Docker

Le frontend peut être démarré via Docker Compose depuis la racine du projet :

```bash
# Démarrage de tous les services
docker compose up -d

# Rebuild du frontend uniquement
./manage.sh rebuild frontend
```
