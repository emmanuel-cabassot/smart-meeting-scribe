# 🚀 Phase 1 - MVP Core

> **Objectif** : Application fonctionnelle avec login, upload audio/vidéo, et visualisation des transcriptions.

---

## 📊 Vue d'ensemble

| Info | Valeur |
|------|--------|
| **Durée estimée** | ~1.5 semaines (base existante) |
| **Statut** | 🔄 En cours (~65% fait) |
| **Dépendances** | Backend API fonctionnel ✅ |
| **Code source** | `03-interface/frontend-nextjs/` |

---

## ✅ Ce qui existe déjà

Le projet a une base fonctionnelle :

| Élément | Fichier | Status |
|---------|---------|--------|
| Next.js 16 + React 19 | `package.json` | ✅ |
| Tailwind 4 | `postcss.config.mjs` | ✅ |
| Docker multi-stage | `Dockerfile` | ✅ |
| Docker Compose | `../docker-compose.yml` | ✅ |
| Upload avec XHR progress | `hooks/use-upload.ts` | ✅ |
| Polling status | `hooks/use-polling.ts` | ✅ |
| Drag & Drop zone | `components/VideoUpload.tsx` | ✅ |
| Viewer transcription | `components/TranscriptionViewer.tsx` | ✅ |
| Fonction cn() | `lib/utils.ts` | ✅ |
| Lucide Icons | `package.json` | ✅ |

---

## ✅ Checklist détaillée

### 1. Setup Projet ~~(0.5 jour)~~ → FAIT

- [x] Créer le projet Next.js 16 ✅ Existe dans `03-interface/frontend-nextjs/`
- [x] Initialiser shadcn/ui ✅ Composants créés manuellement dans `components/ui/`
- [x] Configurer le thème dark (globals.css) ✅ Design system complet
- [x] Ajouter les fonts (Inter, JetBrains Mono) ✅ Dans `layout.tsx`
- [x] Structure de base (`components/`, `lib/`, `hooks/`) ✅ Existe

### 2. Design System & Tokens ~~(0.5 jour)~~ → FAIT

- [x] Configurer les CSS variables dark theme dans `globals.css` ✅
  - Backgrounds (--bg-primary, --bg-secondary, etc.)
  - Accents (--accent-primary, --accent-success, etc.)
  - Text colors, Borders
- [x] Composants shadcn créés : ✅
  - `button.tsx`, `card.tsx`, `input.tsx`, `label.tsx`
  - `badge.tsx`, `progress.tsx`, `dialog.tsx`
  - `dropdown-menu.tsx`, `toast.tsx`, `toaster.tsx`
- [x] `lib/utils.ts` avec `cn()`, `formatDate()`, `formatDuration()` ✅

### 3. Layout Principal ~~(1 jour)~~ → FAIT

- [x] `components/layout/MainLayout.tsx` - Structure 3 zones ✅
- [x] `components/layout/Sidebar.tsx` - Navigation avec groupes ✅
- [x] `components/layout/TopHeader.tsx` - Search + Upload button + User dropdown ✅
- [x] `components/layout/UserDropdown.tsx` - Menu utilisateur (settings, logout) ✅
- [x] `components/layout/Breadcrumb.tsx` - Fil d'ariane ✅
- [x] `app/(dashboard)/layout.tsx` - Layout protégé avec MainLayout ✅
- [x] `app/(dashboard)/page.tsx` - Dashboard avec empty state ✅

### 4. Authentification (1 jour)

- [x] `lib/api.ts` - Wrapper fetch avec gestion token ✅
- [x] `lib/upload.ts` - Upload avec progress ✅ Existe (`hooks/use-upload.ts`)
- [x] `stores/auth-store.ts` - Zustand store (token, user, isAuthenticated) ✅
- [x] `hooks/use-auth.ts` - Hook login/logout/register ✅
- [x] `types/` - Types TypeScript (user.ts, meeting.ts, group.ts) ✅
- [x] `app/(auth)/login/page.tsx` - Page login ✅
- [x] `app/(auth)/register/page.tsx` - Page register ✅
- [x] `app/(auth)/layout.tsx` - Layout centré pour auth ✅
- [ ] Middleware ou guard pour routes protégées

### 5. Dashboard & Smart Cards (1 jour)

- [ ] `types/meeting.ts` - Types Meeting, MeetingStatus
- [ ] `types/group.ts` - Types Group, GroupType
- [ ] `hooks/use-meetings.ts` - React Query pour les meetings
- [ ] `hooks/use-groups.ts` - React Query pour les groupes
- [ ] `components/common/StatusBadge.tsx` - Badge de statut
- [ ] `components/common/GroupBadge.tsx` - Badge type groupe
- [ ] `components/features/meetings/SmartCard.tsx` - Card meeting (évolution de VideoUpload)
- [ ] `components/features/meetings/MeetingCardSkeleton.tsx` - Skeleton loading
- [ ] `app/(dashboard)/page.tsx` - Dashboard avec liste des cards
- [x] Polling pour status updates ✅ Existe (`hooks/use-polling.ts`)

### 6. Upload - Amélioration ~~(0.5 jour)~~ → FAIT

- [x] Drag & drop zone ✅ (page V0 intégrée)
- [x] GroupSelector multi-select groupes ✅ (intégré dans page upload)
- [x] Barre de progression ✅
- [x] Hook upload avec progress ✅
- [x] Envoyer `group_ids` avec l'upload ✅
- [x] `app/(dashboard)/upload/page.tsx` - Page upload dédiée ✅ (générée par V0)
- [x] Validation fichier type ✅
- [x] Validation taille max 2GB ✅

### 7. Détail Meeting (1 jour)

- [ ] `components/common/MediaPlayer.tsx` - Wrapper HTML5 audio/video
- [x] Vue transcription ✅ Existe (`components/TranscriptionViewer.tsx`)
- [ ] **ADAPTER** : `TranscriptView.tsx` - Style timeline avec speakers
- [ ] `components/features/meetings/AIInsights.tsx` - Encart résumé
- [ ] `app/(dashboard)/meetings/[id]/page.tsx` - Page détail
- [ ] Affichage metadata (durée, date, speakers, groupes)

### 8. Actions Meeting (0.5 jour)

- [ ] Modal "Edit Title" (dialog shadcn)
- [ ] Modal "Delete Confirmation" (dialog shadcn)
- [ ] Dropdown menu [⋯ More] sur les cards
- [ ] API calls pour PATCH et DELETE

### 9. Settings (0.5 jour)

- [ ] `app/(dashboard)/settings/page.tsx` - Page simple
- [ ] Afficher profil (nom, email) en read-only
- [ ] Placeholder pour futures fonctionnalités

### 10. Tests & Polish (0.5 jour)

- [ ] Tester le flow complet : Login → Upload → Voir transcription
- [ ] Vérifier les toasts (succès, erreur)
- [ ] Vérifier les empty states
- [ ] Vérifier les loading states
- [ ] Fix bugs découverts
- [ ] Micro-animations (hover, transitions)

---

## 🚦 Critères de succès

À la fin de la Phase 1, je dois pouvoir :

- [ ] Me connecter avec email/password
- [ ] Créer un compte
- [ ] Voir la liste des meetings (groupée par date)
- [ ] Uploader un fichier audio/vidéo avec sélection de groupes
- [x] Voir la progression de l'upload ✅
- [x] Voir le statut de transcription (pending → completed) ✅
- [x] Lire la transcription finale ✅
- [ ] Écouter/regarder le média
- [ ] Modifier le titre d'un meeting
- [ ] Supprimer un meeting
- [ ] Me déconnecter

---

## ⚠️ Hors scope Phase 1

Ces features sont explicitement reportées :

- ❌ Recherche avancée / Command Palette
- ❌ Filtres par groupe/status/date
- ❌ RAG Chat
- ❌ Download transcription (TXT, JSON)
- ❌ CRUD Groupes (Admin)
- ❌ Responsive mobile
- ❌ Tests automatisés (E2E)

---

## 📝 Notes de développement

### Structure actuelle vs cible

Le code existant est une **page unique** qui fait tout. Pour le MVP, on doit :
1. Ajouter l'authentification (login/register)
2. Créer le layout avec sidebar
3. Transformer la page en dashboard avec cards
4. Ajouter la sélection de groupes à l'upload
5. Créer une page détail pour chaque meeting

### Fichiers à adapter (pas supprimer)

| Fichier existant | Action |
|------------------|--------|
| `components/VideoUpload.tsx` | Adapter → ajouter GroupSelector |
| `components/TranscriptionViewer.tsx` | Adapter → style timeline |
| `hooks/use-upload.ts` | Adapter → envoyer group_ids |
| `hooks/use-polling.ts` | Garder tel quel |
| `app/page.tsx` | Transformer en dashboard |

---

*Dernière mise à jour : 17 Janvier 2026*
