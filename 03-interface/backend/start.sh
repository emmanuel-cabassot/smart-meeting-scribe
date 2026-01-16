#!/bin/bash
set -e

echo "🚀 Starting Smart Meeting Scribe API..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h sms_postgres -p 5432 -U ${POSTGRES_USER:-postgres} -q; do
    sleep 1
done
echo "✅ PostgreSQL is ready!"

# Run Alembic migrations
echo "📦 Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete!"

# Run database initialization (seed data)
echo "🌱 Initializing database with seed data..."
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.db.init_db import init_db

async def main():
    async with AsyncSessionLocal() as session:
        await init_db(session)

asyncio.run(main())
"
echo "✅ Database initialized!"

# Start the application
echo "🎯 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
