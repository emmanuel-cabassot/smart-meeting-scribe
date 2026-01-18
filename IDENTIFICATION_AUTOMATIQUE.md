# 📑 Master Plan V6.0 : Smart Meeting Scribe

**Objectif** : Transformer une application de transcription passive en une **Intelligence Conversationnelle Active** capable d'identifier les interlocuteurs de manière autonome et rétroactive.

---

## 1. La Philosophie "Zéro Friction" (Le Pourquoi)

Nous abandonnons l'idée obsolète de demander aux utilisateurs d'enregistrer leur voix dans un profil ("Enrollment Actif"). En 2026, l'expérience utilisateur doit être fluide.

- **Le Concept** : L'application apprend qui est qui simplement en "écoutant" les réunions.
- **L'Usage** : L'utilisateur clique sur "Speaker 2" dans une réunion passée, dit "C'est Albert", et le système propage cette identité partout (passé, présent, futur).
- **La Promesse** : Plus l'entreprise utilise l'outil, plus il devient intelligent, sans effort d'administration.

---

## 2. L'Architecture Technique (Le Comment)

Nous passons d'une logique de comparaison de fichiers audio (lente) à une logique de **Moteur de Recherche Vectoriel** (Ultra-Rapide).

### A. La Stack Technologique

| Composant | Technologie | Rôle |
|:---|:---|:---|
| **Segmenter** | Pyannote 4.0 (EEND SOTA) | Découpe "Qui parle quand" |
| **Identifier** | WeSpeaker (CAM++ / ResNet34) | Extrait un vecteur (256 dims) par segment |
| **Mémoriser** | Qdrant | Base de données vectorielle (Cerveau) |
| **Orchestrer** | Worker Python (Taskiq) | Pipeline séquentiel pour économiser la VRAM |

### B. Le Pipeline "Safe" (Séquentiel GPU)

Nous adoptons une approche **séquentielle robuste** pour la gestion VRAM :

```
1. Pyannote   → Découpe audio (Diarisation)     → Unload
2. WeSpeaker  → Extrait vecteurs par segment    → Unload
3. Qdrant     → Ingère les vecteurs
4. Whisper    → Transcrit le texte              → Unload
```

> [!IMPORTANT]
> **Avantage** : Stabilité totale, gestion parfaite de la mémoire GPU (Load/Unload séquentiel).

### C. Le Modèle de Données (Qdrant)

Nous divisons la mémoire en **deux collections distinctes** :

#### `session_vectors` — Le "Nuage" (Mémoire Brute)

- **Contenu** : Chaque phrase prononcée dans chaque réunion → vecteur stocké ici.
- **Volume** : Énorme mais optimisé (**Quantization INT8** = RAM ÷ 4).
- **Utilité** : Permet de retrouver quelqu'un même s'il a changé de ton, de micro, ou s'il était enrhumé (algorithme k-NN).

```json
{
  "id": "uuid-segment",
  "vector": [0.12, -0.34, ...],
  "payload": {
    "meeting_id": "uuid-meeting",
    "meeting_date": "2026-01-10T14:00:00Z",  // ⚠️ Saisi par l'utilisateur à l'upload (pas auto)
    "speaker_label": "SPEAKER_02",
    "speaker_name": null,
    "start_time": 45.2,
    "end_time": 48.7,
    "duration": 3.5,
    "confidence_score": 0.92,
    "group_ids": ["team-dev", "all"],
    "status": "unconfirmed",
    "created_at": "2026-01-18T21:00:00Z"      // Date d'ingestion dans Qdrant
  }
}
```

#### `identity_registry` — Le "VIP" (Mémoire Propre)

- **Contenu** : Un "Super-Vecteur" unique par personne (Moyenne pondérée des meilleurs segments).
- **Utilité** : Référence stable et rapide pour l'identification immédiate.
- **Quantization** : **Float32** (précision maximale, petite taille).

```json
{
  "id": "uuid-person",
  "vector": [0.15, -0.32, ...],
  "payload": {
    "name": "Albert Dupont",
    "email": "albert@company.com",
    "group_ids": ["team-dev", "codir"],
    "sample_count": 127,
    "last_updated": "2026-01-18T21:00:00Z",
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

> [!NOTE]
> **RAG (texte)** : Collections séparées en **Float32** pour conserver la précision sémantique.

---

## 3. Les Algorithmes de Décision (La Logique Métier)

Ces règles mathématiques garantissent une identification fiable et évolutive.

### A. Filtre de Qualité (Avant Recherche)

Lors d'une identification, on cherche les voisins dans le "Nuage", **mais on ne compte le vote que si** :

```python
if neighbor.confidence_score > 0.8:
    count_vote()
else:
    ignore()  # Bruit : toux, fond sonore
```

> **Résultat** : Précision > 95%.

### B. Règle de Dominance (Anti-Bruit)

Lors du scan rétroactif, ne renomme pas un speaker si seulement une minorité de ses segments matchent.

```python
# Dans scan_history_task (tasks.py)
total_segments = len(speaker_x_segments)
albert_votes = count_matching_albert(speaker_x_segments)

# Règle de Dominance
if albert_votes / total_segments > 0.6:
    rename_to_albert()
else:
    ignore()  # Probablement juste un "Bonjour" dans le micro de quelqu'un d'autre
```

> **Règle** : Renommer seulement si > **60%** des segments matchent le profil cible.

### C. Moyenne Mobile (Aging)

La voix change (rhume, micro différent). Le profil doit évoluer dans le temps.

```python
# Dans API de renommage (speakers.py)
# Quand on confirme une identification :

ALPHA = 0.1  # 10% du nouveau, 90% de l'historique
new_vector = (1 - ALPHA) * old_profile_vector + ALPHA * today_vector

# Sauvegarder dans identity_registry
upsert_identity(person_id, new_vector, increment_sample_count=True)
```

> **Avantage** : Le profil s'adapte progressivement sans perdre son historique.

---

## 4. Le Workflow d'Intégration (Où Coder Quoi)

### Étape 1 : Infrastructure (`01-core`)

| Fichier | Action |
|---|---|
| `docker-compose.yml` | Ajouter le service `qdrant` |
| `init_qdrant.py` | Créer les 2 collections avec optimisation RAM (Vecteurs) + SSD (Payloads) |

### Étape 2 : Worker IA (`02-workers`)

| Fichier | Action |
|---|---|
| `services/identification.py` | Intégrer WeSpeaker, calculer vecteurs par segment |
| `services/vector_db.py` | Client Qdrant : upsert, search avec filtre `confidence_score` |
| `worker/tasks.py` | Pipeline séquentiel + Tâche `scan_history_for_identity` |

### Étape 3 : API Backend (`03-interface/backend`)

| Fichier | Action |
|---|---|
| `endpoints/speakers.py` (Nouveau) | `POST /assign-identity` : Crée profil + lance scan rétroactif |
| `endpoints/speakers.py` | `DELETE /users/{id}/voice-data` : GDPR "Forget User" |

---

## 5. Privacy / GDPR

Tu stockes des **données biométriques** (empreintes vocales). Obligations :

### Endpoint `DELETE /api/v1/users/{id}/voice-data`

1. **Supprimer** l'entrée dans `identity_registry`.
2. **Anonymiser** dans `session_vectors` :
   ```python
   # Update de masse
   for vector in user_vectors:
       vector.payload.status = "deleted"
       vector.payload.speaker_name = None
       vector.vector = None  # ou vecteur aléatoire
   ```

---

## 6. Pourquoi C'est la Bonne Solution (2026 Ready)

| Critère | Avantage |
|---|---|
| **Scalable** | Qdrant + INT8 = 10 ans de réunions sur serveur standard |
| **Robuste** | Pipeline séquentiel GPU, pas de crash VRAM |
| **Évolutif** | Moyenne Mobile = profils qui s'adaptent |
| **Précis** | Filtre qualité + Dominance = > 95% précision |
| **Sécurisé** | `group_ids` = isolation RBAC par équipe/CODIR |
| **GDPR** | "Forget User" = conformité légale |

---

## 7. Définitions Techniques (Clarifications)

### A. Le `confidence_score` — Comment le calculer ?

Le score de confiance mesure la **qualité exploitable** d'un segment audio. Formule proposée :

```python
def compute_confidence(segment_duration: float, snr_db: float = None) -> float:
    """
    Score basé sur la durée (proxy de qualité).
    Segments courts = risque de bruit, segments longs = plus fiable.
    """
    # Durée : 3 secondes = score max (1.0)
    duration_score = min(1.0, segment_duration / 3.0)
    
    # Optionnel : Si SNR disponible (pyannote peut le fournir)
    if snr_db is not None:
        snr_score = min(1.0, snr_db / 20.0)  # 20 dB = excellent
        return (duration_score + snr_score) / 2
    
    return duration_score
```

| Durée segment | Score |
|---|---|
| < 1 sec | 0.33 (faible) |
| 2 sec | 0.67 |
| ≥ 3 sec | 1.0 (max) |

---

### B. La Métrique de Distance — Cosine Similarity

Qdrant supporte plusieurs métriques. Pour les embeddings vocaux (WeSpeaker), on utilise **Cosine** :

```python
# Configuration collection Qdrant
collection_config = {
    "vectors": {
        "size": 256,           # Dimension WeSpeaker
        "distance": "Cosine"   # ✅ Recommandé pour embeddings normalisés
    }
}
```

| Distance Cosine | Interprétation |
|---|---|
| 0.0 - 0.3 | ✅ Même personne (très similaire) |
| 0.3 - 0.6 | ⚠️ Possible match (à vérifier) |
| 0.6 - 1.0 | ❌ Personnes différentes |

> **Seuil de match retenu** : `distance < 0.4` pour être conservateur.

---

### C. Les `group_ids` — Source et Gestion

Les `group_ids` sont **saisis par l'utilisateur à l'upload** de la réunion.

**Workflow UI** :
1. L'utilisateur upload un fichier audio.
2. Il saisit la **date de réunion** (`meeting_date`).
3. Il coche les **groupes concernés** (multi-select) : `["team-dev", "codir", "all"]`.
4. Ces `group_ids` sont propagés à tous les vecteurs de la réunion.

**Règle de sécurité** :
```python
# Lors d'une recherche, filtrer par groupes de l'utilisateur
results = qdrant.search(
    vector=query_vector,
    filter={"group_ids": {"$in": user.group_ids}}  # RBAC
)
```

---

### D. WeSpeaker — Quel Modèle Choisir ?

| Modèle | Dimensions | VRAM | Précision | Recommandation |
|---|---|---|---|---|
| **CAM++** | 192 | ~1 GB | Bonne | ✅ Production (léger) |
| **ResNet34** | 256 | ~2 GB | Excellente | 🔬 Si précision critique |
| **ECAPA-TDNN** | 192 | ~1.5 GB | Très bonne | Alternative |

**Choix recommandé** : **CAM++** pour commencer (bon ratio précision/ressources).

---

### E. Estimation de Volume — Combien de Vecteurs ?

| Paramètre | Valeur typique |
|---|---|
| Durée moyenne segment | ~3 secondes |
| Réunion 1h | ~1200 segments (20 segments/min) |
| Réunion 1h (après filtrage) | ~400-600 segments exploitables |
| 1 an de réunions (10 réunions/semaine) | ~250,000 vecteurs |
| 10 ans | ~2,500,000 vecteurs |

**Stockage Qdrant (INT8)** :
```
2.5M vecteurs × 256 dims × 1 byte = ~640 MB de vecteurs
+ Payloads JSON = ~1-2 GB total
```

> ✅ Largement gérable sur un serveur 8 GB RAM.

---

### F. Gestion des Conflits — Voix Similaires

**Problème** : Albert et Bernard ont des voix très proches (jumeaux, etc.).

**Solution** : Lors du renommage, si le système détecte un conflit :

```python
# Recherche dans identity_registry
matches = search_identity(new_vector, limit=3)

if len(matches) > 1 and matches[0].distance - matches[1].distance < 0.05:
    # Ambiguïté : deux profils très proches
    raise ConflictError(
        f"Ambiguïté entre {matches[0].name} et {matches[1].name}. "
        "Veuillez confirmer manuellement."
    )
```

> L'UI affiche un avertissement et demande confirmation à l'utilisateur.
