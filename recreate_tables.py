"""
Recreate database tables to match current models
WARNING: This will DELETE all existing data!
"""

import asyncio
from app.core.database import engine, Base
from app.models import *  # Import all models

async def recreate_tables():
    print("🗑️  Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("✅ Tables dropped")

    print("📦 Creating tables from models...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tables created successfully!")
    print("\nNew schema matches the code now.")

if __name__ == "__main__":
    asyncio.run(recreate_tables())
