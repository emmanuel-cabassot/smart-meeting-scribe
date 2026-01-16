from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
from app.core.config import settings

# On initialise le Broker
broker = ListQueueBroker(
    url=settings.REDIS_URL,
).with_result_backend(
    RedisAsyncResultBackend(redis_url=settings.REDIS_URL)
)

# CORRECTION : On définit une vraie fonction Python (vide)
# Le décorateur va la transformer en objet Tâche avec la méthode .kiq()
@broker.task(task_name="process_transcription_full")
def kicker(file_path: str, meeting_id: str):
    pass
