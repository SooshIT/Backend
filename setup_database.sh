#!/bin/bash
# Database Setup Script for Soosh Backend
# This script installs required PostgreSQL extensions and sets up the database

set -e  # Exit on error

echo "🔧 Soosh Database Setup"
echo "======================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check PostgreSQL version
echo "📋 Checking PostgreSQL version..."
PG_VERSION=$(psql --version | grep -oE '[0-9]+' | head -1)
echo "   PostgreSQL version: $PG_VERSION"
echo ""

# Install pgvector
echo "📦 Installing pgvector extension..."
if ! brew list pgvector &>/dev/null; then
    echo "   Installing pgvector via Homebrew..."
    brew install pgvector
else
    echo "   ✅ pgvector already installed"
fi
echo ""

# Install PostGIS
echo "📦 Installing PostGIS extension..."
if ! brew list postgis &>/dev/null; then
    echo "   Installing PostGIS via Homebrew..."
    brew install postgis
else
    echo "   ✅ PostGIS already installed"
fi
echo ""

# Drop and recreate database
echo "🗑️  Dropping existing database (if exists)..."
psql postgres -c "DROP DATABASE IF EXISTS soosh;" 2>/dev/null || true
echo "   ✅ Old database dropped"
echo ""

echo "🆕 Creating fresh database..."
psql postgres -c "CREATE DATABASE soosh;"
echo "   ✅ Database created"
echo ""

# Run schema
echo "📝 Running database schema..."
psql soosh < database_schema.sql
echo ""

# Check if it worked
echo "✅ Database setup complete!"
echo ""
echo "📊 Verifying database tables..."
TABLE_COUNT=$(psql soosh -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "   Tables created: $TABLE_COUNT"
echo ""

echo "🎉 All done! Your database is ready."
echo ""
echo "Next steps:"
echo "  1. Update backend/.env with your database credentials"
echo "  2. Start the backend: uvicorn main:app --reload"
