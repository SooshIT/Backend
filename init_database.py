"""
Database initialization script
Runs the complete database schema on startup
"""
import asyncio
import asyncpg
from app.core.config import settings
from loguru import logger


async def init_database():
    """Initialize database with complete schema"""
    try:
        # Read the SQL schema file
        with open('complete_database_schema.sql', 'r') as f:
            schema_sql = f.read()

        logger.info("📚 Connecting to database...")

        # Extract connection string without the +asyncpg part
        db_url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

        # Connect to database
        conn = await asyncpg.connect(db_url)

        logger.info("🚀 Running database schema...")

        # Execute the schema
        await conn.execute(schema_sql)

        logger.info("✅ Database schema initialized successfully!")

        await conn.close()

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
