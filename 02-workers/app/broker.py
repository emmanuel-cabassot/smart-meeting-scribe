import multiprocessing
# On utilise les imports spécifiques à la version 1.2.1+
from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker
from app.core.config import settings

# 🚨 SÉCURITÉ GPU (Mode Spawn obligatoire pour Torch/CUDA)
try:
    multiprocessing.set_start_method("spawn", force=True)
except RuntimeError:
    pass

# 1. Initialisation du Broker avec la nouvelle classe ListQueueBroker
broker = ListQueueBroker(
    url=settings.REDIS_URL,
).with_result_backend(
    RedisAsyncResultBackend(redis_url=settings.REDIS_URL)
)

# 2. Cycle de vie
@broker.on_event("startup")
async def startup_event(state):
    print("🚀 [Taskiq 0.12.1] Worker démarré")
    print(f"🔌 Transport: Redis List Queue sur {settings.REDIS_URL}")

# 3. Importation des tâches pour enregistrement
import app.worker.tasks