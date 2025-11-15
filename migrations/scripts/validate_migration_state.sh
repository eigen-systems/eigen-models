#!/bin/bash

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Determine which environment to use (default: dev)
ENV_FILE=".env.dev"
ENV_NAME="dev"

# Check for environment flag from ENV variable or command line
if [ "$ENV" = "prod" ] || [ "$1" = "--prod" ]; then
    ENV_FILE=".env.prod"
    ENV_NAME="prod"
fi

# Auto-source environment file if it exists
if [ -f "$ENV_FILE" ]; then
    echo "🔧 Loading environment variables from $ENV_FILE ($ENV_NAME)..."
    source "$ENV_FILE"
else
    echo "⚠️  Warning: $ENV_FILE not found"
    exit 1
fi

# Auto-activate virtual environment if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

echo "🔍 Validating Migration State..."
echo "================================="

# Get current database revision (run alembic from migrations directory)
echo "📊 Database State:"
DB_REVISION=$(cd migrations && alembic current 2>/dev/null | grep -v INFO | grep -v "Context impl" | grep -v "Will assume" | tail -n1 | awk '{print $1}')
echo "   Current: $DB_REVISION"

# Get latest migration file revision
echo ""
echo "📁 Migration Files:"
HEAD_REVISION=$(cd migrations && alembic heads 2>/dev/null | grep -v INFO | tail -n1 | awk '{print $1}')
echo "   Head: $HEAD_REVISION"

# Check if they match
echo ""
echo "🔍 Validation:"
if [ "$DB_REVISION" = "$HEAD_REVISION" ]; then
    echo "   ✅ SYNCHRONIZED - Database matches migration files"
    echo "   👍 Ready for new migrations"
    exit 0
elif [ -z "$DB_REVISION" ]; then
    echo "   ⚠️  DATABASE NOT INITIALIZED"
    echo "   🔧 Run: cd migrations && alembic upgrade head"
    exit 1
else
    echo "   ❌ MISMATCH DETECTED!"
    echo "   Database: $DB_REVISION"
    echo "   Files:    $HEAD_REVISION"
    echo ""
    echo "🔧 Quick Fixes:"
    echo "   1. Apply pending migrations: make migrate"
    echo "   2. If that fails, check migration history: make history"
    echo "   3. If revision missing, contact team for migration sync"
    exit 1
fi 