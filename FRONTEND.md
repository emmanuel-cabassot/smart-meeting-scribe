# 🎨 Frontend Documentation - Smart Meeting Scribe

> **Smart Meeting Scribe** transcrit automatiquement des fichiers audio/vidéo de réunions avec identification des locuteurs (Whisper + Pyannote).
> Ce fichier est le **point d'entrée** pour comprendre et travailler sur le frontend.

**Branche active** : `front` | **Pour lancer** : `./manage.sh front-dev`

---

## 📁 Code source

Le frontend existe déjà dans : **`03-interface/frontend-nextjs/`**

| Élément | Status |
|---------|--------|
| Next.js 16 + React 19 | ✅ Installé |
| Tailwind 4 | ✅ Configuré |
| Docker + Docker Compose | ✅ Prêt |
| Upload avec progress | ✅ Fonctionnel |
| Polling status | ✅ Fonctionnel |

---

## 📁 Structure de la documentation

| Fichier | Description | Quand le lire |
|---------|-------------|---------------|
| [FRONTEND.md](./FRONTEND.md) | **Ce fichier** - Index et organisation | En premier |
| [FRONTEND_ROADMAP.md](./FRONTEND_ROADMAP.md) | Vision, Design System, Architecture, Stack, API | Pour comprendre le "quoi" et "comment" |
| [FRONTEND_DECISIONS.md](./FRONTEND_DECISIONS.md) | Journal des décisions clés et leur justification | Pour comprendre le "pourquoi" |
| [FRONTEND_PHASE1_MVP.md](./FRONTEND_PHASE1_MVP.md) | Checklist détaillée Phase 1 (MVP) | Pour implémenter Phase 1 |
| FRONTEND_PHASE2_UX.md | Checklist Phase 2 (à créer) | Après Phase 1 |
| FRONTEND_PHASE3_RAG.md | Checklist Phase 3 (à créer) | Après Phase 2 |

---

## 🎯 Pour une IA qui travaille sur le frontend

### Si tu dois comprendre le projet :
1. Explore d'abord le code existant dans `03-interface/frontend-nextjs/src/`
2. Lis `FRONTEND_ROADMAP.md` pour la vision globale et l'architecture cible
3. Lis `FRONTEND_DECISIONS.md` pour comprendre les choix techniques

### Si tu dois implémenter :
1. Lis le fichier de la phase en cours (`FRONTEND_PHASE1_MVP.md`)
2. Les tâches marquées [x] sont déjà faites
3. Coche les tâches au fur et à mesure
4. Référence `FRONTEND_ROADMAP.md` pour les détails techniques

### Si tu dois prendre une décision :
1. Documente-la dans `FRONTEND_DECISIONS.md` avec le format [Dxxx]
2. Mets à jour le roadmap si nécessaire

---

## 📊 État actuel

| Phase | Status | Fichier |
|-------|--------|---------|
| **Phase 1 - MVP Core** | 🔄 En cours (~50% fait) | `FRONTEND_PHASE1_MVP.md` |
| Phase 2 - Enhanced UX | ⏳ À venir | - |
| Phase 3 - RAG Chat | ⏳ À venir | - |

---

## 🔗 Liens utiles

- **Code Frontend** : `03-interface/frontend-nextjs/`
- **Backend API** : `03-interface/backend/`
- **📡 Routes API** : [`03-interface/backend/README.md`](./03-interface/backend/README.md) ← Documentation complète des endpoints
- **Architecture globale** : `ARCHITECTURE.md`
- **Contexte projet** : `CONTEXT.md`

---

## 🌐 URLs de développement

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Interface Next.js |
| Backend API | http://localhost:5000 | FastAPI |
| API Docs | http://localhost:5000/docs | Swagger UI |

---
## PARLE EN FRANCAIS
## Quand tu fais une nouvelle page demande moi de te donner un exemple ave v0.app
*Dernière mise à jour : 17 Janvier 2026*
