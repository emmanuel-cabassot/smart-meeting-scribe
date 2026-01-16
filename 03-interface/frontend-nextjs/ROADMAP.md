# 🚀 Frontend Roadmap - Smart Meeting Scribe

## Vision
Créer une interface moderne permettant aux utilisateurs de transcire, organiser et exploiter leurs réunions grâce à l'IA.

---

## Phase 1 : MVP Fonctionnel (Week 1)

### Objectif
Une application fonctionnelle end-to-end : login → upload → voir résultats.

### Pages

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | Formulaire email/password → JWT |
| Layout | `layout.tsx` | Sidebar (Services/Projets) + Header |
| Feed | `/` | Liste des meetings visibles |
| Upload | `/upload` | Dropzone + tagging Service/Projet |
| Meeting Detail | `/meeting/[id]` | Player basique + transcript JSON |

### Composants clés

- [ ] `<Sidebar>` : Navigation Services + Projets (depuis `/users/me`)
- [ ] `<MeetingCard>` : Carte réunion (titre, date, service, status)
- [ ] `<UploadDropzone>` : Glisser-déposer fichiers audio/vidéo
- [ ] `<TranscriptViewer>` : Affichage du JSON fusion

### Backend requis

| Endpoint | Status | Description |
|----------|--------|-------------|
| `POST /auth/login` | ✅ OK | Authentification |
| `GET /users/me` | ✅ OK | Contexte utilisateur |
| `GET /meetings/` | ✅ OK | Liste avec filtres |
| `POST /process/` | ✅ OK | Upload avec auth |
| `GET /meetings/{id}` | ✅ OK | Détail meeting |

---

## Phase 2 : Experience Enrichie (Week 2)

### Objectif
Améliorer l'UX avec un player audio synchronisé et de la recherche.

### Pages

| Page | Route | Description |
|------|-------|-------------|
| Projects | `/projects/[id]` | Feed filtré par projet |
| Teams | `/teams/[id]` | Feed filtré par service |
| Settings | `/settings` | Voice Bank + profil |

### Composants clés

- [ ] `<AudioPlayer>` : Waveform interactive avec contrôles
- [ ] `<SyncTranscript>` : Transcript synchronisé (style karaoké)
- [ ] `<SearchBar>` : Recherche dans les meetings
- [ ] `<FilterPanel>` : Filtres service/projet/date

### Backend requis

| Endpoint | Status | Description |
|----------|--------|-------------|
| `GET /meetings/?search=` | ⏳ TODO | Recherche texte |
| Transcription en DB | ⏳ TODO | Pour recherche full-text |

---

## Phase 3 : Intelligence IA (V6)

### Objectif
Intégrer un LLM pour générer des insights et permettre le chat RAG.

### Pages

| Page | Route | Description |
|------|-------|-------------|
| Ask AI | Drawer global | Chat contextuel |

### Fonctionnalités

- [ ] "Ask AI" drawer (volet latéral droit)
- [ ] Résumé automatique (Summary)
- [ ] Détection d'action items
- [ ] Analyse de sentiment
- [ ] "My Mentions" (quand on dit ton nom)
- [ ] Chat RAG avec citations audio

### Backend requis

| Endpoint | Status | Description |
|----------|--------|-------------|
| `POST /ai/chat` | ❌ TODO | Chat RAG |
| `GET /ai/summary/{id}` | ❌ TODO | Résumé IA |
| Qdrant indexation | ❌ TODO | Vectorisation transcriptions |

---

## Stack Technique

| Technologie | Usage |
|-------------|-------|
| **Next.js 16** | App Router, SSR |
| **TypeScript** | Typage strict |
| **Tailwind CSS** | Styling |
| **shadcn/ui** | Composants UI |
| **React Query** | Gestion du state serveur |
| **Zustand** | State global (auth, user) |

---

## Structure Dossiers

```
src/app/
├── layout.tsx              # Sidebar + Header
├── page.tsx                # Feed principal
├── login/page.tsx          # Page login
├── upload/page.tsx         # Upload meeting
├── meeting/[id]/page.tsx   # Détail meeting
├── projects/[id]/page.tsx  # Feed projet
├── teams/[id]/page.tsx     # Feed service
└── settings/page.tsx       # Voice Bank
```

---

## Priorités Phase 1

1. **Login fonctionnel** (stocker JWT)
2. **Layout avec sidebar** (afficher services/projets depuis API)
3. **Liste meetings** (appeler GET /meetings/)
4. **Upload** (POST /process/ avec token)
5. **Afficher transcript** (récupérer fusion.json depuis S3)

---

*Dernière mise à jour : 17 Janvier 2026*
