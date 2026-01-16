# 🎨 Frontend - Next.js 16

Interface utilisateur pour Smart Meeting Scribe.

## 🏗️ Stack

- **Next.js 16** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Docker Standalone** (~100MB)

## 📂 Structure

```
src/
├── app/
│   ├── page.tsx             # Page principale (upload + résultats)
│   ├── layout.tsx           # Layout global
│   └── globals.css          # Styles Tailwind
├── components/              # Composants réutilisables
└── lib/                     # Utilitaires
```

## 🚀 Développement

```bash
npm install
npm run dev
```

Accès : http://localhost:3000

## 🐳 Docker (Production)

```bash
docker build -t sms-frontend .
docker run -p 3000:3000 sms-frontend
```

Le build utilise le mode **standalone** de Next.js pour une image optimisée.

## 🔗 API Backend

Le frontend communique avec l'API via :
- `POST /api/v1/process/` - Upload audio
- `GET /api/v1/process/status/{task_id}` - Polling résultats

Variable d'environnement : `NEXT_PUBLIC_API_URL`

## 🎯 Fonctionnalités

- [x] Upload de fichiers audio/vidéo
- [x] Affichage du statut (pending → processing → completed)
- [x] Visualisation de la transcription avec speakers
- [ ] Authentification JWT
- [ ] Dashboard utilisateur
