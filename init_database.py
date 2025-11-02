"""
Database initialization script
Runs the complete database schema on startup
"""
import asyncio
import asyncpg
import os


async def init_database():
    """Initialize database with complete schema"""
    try:
        # Read the SQL schema file
        with open('complete_database_schema.sql', 'r') as f:
            schema_sql = f.read()

        print("📚 Connecting to database...")

        # Get database URL from environment
        db_url = os.getenv('DATABASE_URL', '')

        # Extract connection string without the +asyncpg part
        if '+asyncpg://' in db_url:
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

        print(f"📡 Database URL: {db_url[:30]}...")

        # Connect to database
        conn = await asyncpg.connect(db_url)

        print("🚀 Running database schema...")

        # Execute the schema
        await conn.execute(schema_sql)

        print("✅ Database schema initialized successfully!")

        await conn.close()

    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
