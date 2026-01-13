import asyncio
from app.broker import broker

# On définit la signature de la tâche pour que l'API sache comment l'appeler
@broker.task(name="test_task")
async def test_task(a: int, b: int) -> int:
    return a + b

async def main():
    await broker.startup()
    print("🚀 Envoi de la tâche 'test_task' au Worker via Redis...")
    
    # .kiq() envoie le message dans Redis
    kiq = await test_task.kiq(10, 20)
    
    # .wait_result() attend que le Worker renvoie la réponse
    result = await kiq.wait_result()
    
    print(f"✅ Succès ! Le Worker a répondu : {result.return_value}")
    await broker.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
