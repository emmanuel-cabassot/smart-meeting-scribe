"""
Worker Tasks - Point d'entrée central pour toutes les tâches TaskIQ.

Ce module importe et expose toutes les tâches définies dans les sous-modules.
TaskIQ découvrira automatiquement les tâches via ce module.
"""

# === AUDIO TASKS ===
from app.worker.tasks.audio_tasks import process_transcription_full

# === VIDEO TASKS ===
# Importer les tâches vidéo quand elles seront implémentées:
# from app.worker.tasks.video_tasks import process_video_extract_audio

# === OTHER TASKS ===
# from app.worker.tasks.other_tasks import send_notification

__all__ = [
    # Audio
    "process_transcription_full",
    # Video (à ajouter quand implémenté)
]
