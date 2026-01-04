# 🧠 Architecture Technique : Smart Meeting Scribe

Ce document détaille le fonctionnement du pipeline hybride utilisé pour transcrire et identifier les locuteurs (Diarisation) sur le serveur GPU.

## 🔄 Le Flux de Traitement (Pipeline)

Le système ne repose pas sur une seule IA monolithique, mais sur l'orchestration de **deux moteurs spécialisés** qui travaillent en parallèle sur le même fichier audio.



### Étape 1 : Normalisation (FFmpeg)
Avant tout traitement IA, le fichier reçu (m4a, mp3, mp4...) est nettoyé.
* **Action :** Conversion en `.wav`, **16kHz**, **Mono**.
* **Pourquoi ?** Pyannote est extrêmement sensible au taux d'échantillonnage et aux canaux stéréo. Cette étape garantit la stabilité du moteur.

### Étape 2 : Le Détective (Pyannote 3.1)
C'est le module de **Diarisation**.
* **Entrée :** Le fichier WAV propre.
* **Tâche :** Il n'écoute pas les mots, il analyse les empreintes vocales (timbres).
* **Sortie :** Une "Timeline" (Annotation) qui contient des segments temporels associés à des labels anonymes.
    * *Exemple :* `00:00 -> 00:15` = `SPEAKER_00`

### Étape 3 : Le Scribe (Faster-Whisper Large-v3)
C'est le module de **Transcription**.
* **Entrée :** Le même fichier WAV propre.
* **Tâche :** Il transforme l'audio en texte.
* **Sortie :** Des segments de texte avec horodatage, mais sans identité.
    * *Exemple :* `00:00 -> 00:05` = "Bonjour à tous."

### Étape 4 : La Fusion (L'Algorithme de Mapping)
C'est l'étape logique codée en Python (`assign_speaker`). Elle croise les données des étapes 2 et 3.
1.  On prend un segment de texte Whisper (ex: `00:00` à `00:05`).
2.  On regarde dans la Timeline Pyannote qui parlait majoritairement sur cet intervalle.
3.  On attribue le label (ex: `SPEAKER_00`) au texte.

---

## 🛠️ Spécificités Techniques

### Gestion du GPU (NVIDIA Container Toolkit)
* Le conteneur Docker accède directement au GPU via le driver hôte.
* Les calculs sont effectués en **INT8_FLOAT16** pour optimiser la vitesse sans perdre de précision.
* L'option **TF32** (TensorFloat-32) est réactivée pour les cartes RTX série 30xx/40xx.

### Correctifs Appliqués (Patches)
* **PyTorch 2.6 Security Patch :** Surcharge de `torch.load` pour permettre le chargement des poids du modèle Pyannote sans erreur de sécurité (`weights_only=False`).
* **Pyannote Output Wrapper :** Gestion dynamique de l'objet de retour (`DiarizeOutput` vs `Annotation`) pour compatibilité avec les dernières versions de la librairie.