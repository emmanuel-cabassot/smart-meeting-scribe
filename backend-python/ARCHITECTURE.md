# Architecture Backend - Smart Meeting Scribe

## Vue d'ensemble

L'architecture suit le pattern **Clean Architecture** avec 3 couches distinctes :

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                   (Point d'entrée FastAPI)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    api/ (Couche Transport)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   v1/router.py                       │   │
│  │              (Hub central des routes)                │   │
│  └─────────────────────────────────────────────────────┘   │
│                    │                    │                   │
│                    ▼                    ▼                   │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ endpoints/transcribe │  │ endpoints/voice_bank │        │
│  │   POST /process/     │  │  GET /voice-bank/    │        │
│  └──────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 services/ (Couche Métier)                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │   audio    │ │ diarization│ │transcription│              │
│  │ conversion │ │  Pyannote  │ │   Whisper   │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │identification│ │   fusion   │ │  storage   │              │
│  │  WeSpeaker  │ │ merge data │ │ save JSON  │              │
│  └────────────┘ └────────────┘ └────────────┘              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  core/ (Couche Infrastructure)              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │      config.py       │  │      models.py       │        │
│  │  (Variables d'env)   │  │ (Chargement modèles) │        │
│  └──────────────────────┘  └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## Flux de données : Transcription audio

```
Fichier Audio (.mp3, .m4a, etc.)
         │
         ▼
┌─────────────────────┐
│  POST /api/v1/process/  │  ◄── api/v1/endpoints/transcribe.py
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ 1. services/audio   │  Conversion → WAV mono 16kHz
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ 2. services/        │  "Qui parle quand ?"
│    diarization      │  → SPEAKER_00, SPEAKER_01...
└─────────────────────┘
         │ release_models() ← Libère VRAM
         ▼
┌─────────────────────┐
│ 3. services/        │  Associe SPEAKER_XX → "Emmanuel"
│    identification   │  via embeddings voice_bank/
└─────────────────────┘
         │ release_models()
         ▼
┌─────────────────────┐
│ 4. services/        │  "Qu'est-ce qui est dit ?"
│    transcription    │  → Texte avec timestamps
└─────────────────────┘
         │ release_models()
         ▼
┌─────────────────────┐
│ 5. services/fusion  │  Combine texte + speakers
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ 6. services/storage │  Sauvegarde JSON dans recordings/
└─────────────────────┘
         │
         ▼
    { JSON Response }
```

---

## Description des fichiers

### `main.py`
**Rôle** : Point d'entrée de l'application FastAPI.
- Instancie l'app avec métadonnées (titre, version)
- Monte le router API v1 sur `/api/v1`
- Route santé `/` pour vérifier GPU

### `api/v1/router.py`
**Rôle** : Hub centralisant tous les endpoints.
- Importe et branche `transcribe.router` et `voice_bank.router`
- Définit les préfixes (`/process`, `/voice-bank`)
- Configure les tags Swagger

### `api/v1/endpoints/transcribe.py`
**Rôle** : Endpoint principal de traitement audio.
- Reçoit fichier via `UploadFile`
- Orchestre le pipeline : audio → diarisation → identification → transcription → fusion
- Gère la libération VRAM entre chaque étape

### `api/v1/endpoints/voice_bank.py`
**Rôle** : Gestion de la banque de voix.
- Liste les voix enregistrées dans `voice_bank/`

### `services/audio.py`
**Rôle** : Conversion et nettoyage fichiers.
- `convert_to_wav()` : FFmpeg → WAV mono 16kHz
- `cleanup_files()` : Supprime fichiers temporaires

### `services/diarization.py`
**Rôle** : Segmentation par locuteur.
- Utilise Pyannote 3.1
- Retourne une `Annotation` (qui parle quand)

### `services/transcription.py`
**Rôle** : Transcription speech-to-text.
- Utilise Whisper (medium)
- Retourne segments avec timestamps

### `services/identification.py`
**Rôle** : Reconnaissance vocale.
- `get_voice_bank_embeddings()` : Charge embeddings depuis `voice_bank/`
- `identify_speaker()` : Compare via similarité cosinus

### `services/fusion.py`
**Rôle** : Fusion diarisation + transcription.
- Associe chaque segment de texte au locuteur correspondant

### `services/storage.py`
**Rôle** : Persistence des résultats.
- Sauvegarde JSON dans `recordings/`

### `core/models.py`
**Rôle** : Gestionnaire de modèles IA.
- Chargement lazy (à la demande)
- `release_models()` : Libère VRAM (GPU)

### `core/config.py`
**Rôle** : Configuration centralisée.
- Token HuggingFace, chemins, etc.

---

## Routes API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Health check + info GPU |
| POST | `/api/v1/process/` | Transcription audio complète |
| GET | `/api/v1/voice-bank/` | Liste des voix enregistrées |

---

## Gestion VRAM (Optimisation GPU)

Le pipeline charge/décharge les modèles séquentiellement pour éviter les OOM :

```
Pyannote (1.5 GB) → release → WeSpeaker (0.5 GB) → release → Whisper (3 GB) → release
```

Chaque appel à `release_models()` :
1. Supprime les références aux modèles
2. Appelle `torch.cuda.empty_cache()`
3. Force le garbage collector
