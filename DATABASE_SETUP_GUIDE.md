# Database Setup Guide

## Problem

You're getting these errors:
- `could not open extension control file "pgvector.control"` - **pgvector not installed**
- `could not open extension control file "postgis.control"` - **PostGIS not installed**
- `type "geography" does not exist` - Requires PostGIS
- `type "vector" does not exist` - Requires pgvector

## Solution

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
cd /Users/vivekkumar/Soosh/SooshAI/backend
./setup_database.sh
```

This will:
1. Install pgvector via Homebrew
2. Install PostGIS via Homebrew
3. Drop and recreate the database cleanly
4. Run the schema

---

### Option 2: Manual Setup

If the script doesn't work, follow these steps:

#### Step 1: Install pgvector

```bash
# Install via Homebrew
brew install pgvector
```

If that doesn't work, install from source:

```bash
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install  # may need sudo
```

#### Step 2: Install PostGIS

```bash
# Install via Homebrew
brew install postgis
```

#### Step 3: Restart PostgreSQL

```bash
brew services restart postgresql@14
```

#### Step 4: Drop and Recreate Database

```bash
# Connect to postgres database
psql postgres

# Drop existing database
DROP DATABASE IF EXISTS soosh;

# Create fresh database
CREATE DATABASE soosh;

# Exit
\q
```

#### Step 5: Connect and Enable Extensions

```bash
# Connect to soosh database
psql soosh

# Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

# Verify extensions
\dx

# Exit
\q
```

You should see output like:
```
                                      List of installed extensions
   Name    | Version |   Schema   |                        Description
-----------+---------+------------+-----------------------------------------------------------
 pg_trgm   | 1.6     | public     | text similarity measurement and index searching
 postgis   | 3.x.x   | public     | PostGIS geometry and geography spatial types
 uuid-ossp | 1.1     | public     | generate universally unique identifiers (UUIDs)
 vector    | 0.5.1   | public     | vector data type and ivfflat and hnsw access methods
```

#### Step 6: Run Schema

```bash
psql soosh < database_schema.sql
```

---

## Verification

Check that tables were created:

```bash
psql soosh -c "\dt"
```

You should see ~20 tables including:
- users
- categories
- subcategories
- opportunities
- mentor_profiles
- bookings
- payments
- learning_paths
- notifications
- messages
- ai_agents
- etc.

---

## Troubleshooting

### "pgvector not found after brew install"

The extension might be installed for a different PostgreSQL version. Check:

```bash
# Find where pgvector was installed
brew list pgvector

# Find your PostgreSQL data directory
psql postgres -c "SHOW data_directory;"

# Your PostgreSQL version
psql --version
```

If pgvector was installed for PostgreSQL 16 but you're using 14, you need to either:
1. Upgrade to PostgreSQL 16: `brew install postgresql@16`
2. Or compile pgvector specifically for version 14

### "PostGIS not found after brew install"

Similar to pgvector, check the version:

```bash
brew list postgis
```

### Still getting errors?

1. **Completely uninstall and reinstall PostgreSQL**:
   ```bash
   brew uninstall postgresql@14
   brew install postgresql@16
   brew install pgvector
   brew install postgis
   brew services start postgresql@16
   ```

2. **Update your .env file** with the new PostgreSQL connection (if using PostgreSQL 16):
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/soosh
   DATABASE_SYNC_URL=postgresql://postgres:password@localhost:5432/soosh
   ```

---

## Alternative: Use Docker

If you're having persistent issues with local PostgreSQL extensions, use Docker instead:

### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: soosh-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: soosh
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_schema.sql:/docker-entrypoint-initdb.d/schema.sql

volumes:
  postgres_data:
```

### 2. Start PostgreSQL with Docker

```bash
cd /Users/vivekkumar/Soosh/SooshAI/backend
docker-compose up -d
```

This gives you PostgreSQL 16 with pgvector and PostGIS pre-installed!

### 3. Run schema (if not auto-loaded)

```bash
docker exec -i soosh-postgres psql -U postgres -d soosh < database_schema.sql
```

---

## Success!

Once setup is complete, you should be able to:

```bash
# Start backend
cd /Users/vivekkumar/Soosh/SooshAI/backend
uvicorn main:app --reload

# Visit API docs
open http://localhost:8000/api/docs
```

---

## Quick Reference

| Extension | Purpose | Installation |
|-----------|---------|--------------|
| **pgvector** | Vector embeddings for AI recommendations | `brew install pgvector` |
| **PostGIS** | Geospatial features (location-based search) | `brew install postgis` |
| **pg_trgm** | Full-text search | Built-in, just enable |
| **uuid-ossp** | UUID generation | Built-in, just enable |

---

**Need help?** Check the errors carefully and ensure all extensions show up in `\dx` output.
