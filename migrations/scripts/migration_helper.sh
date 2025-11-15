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

# Migration Helper - Comprehensive migration management tool
# This script provides additional utilities for managing migrations with eigen_models

# Function to display help message
show_help() {
    echo "Migration Helper - Comprehensive migration management"
    echo ""
    echo "Usage: ./migration_helper.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  check-models      Validate eigen_models package and imports"
    echo "  check-connection  Test database connection"
    echo "  diff              Show model vs database differences"
    echo "  history           Show migration history"
    echo "  rollback          Rollback to previous migration"
    echo "  reset             Reset database to clean state (DANGEROUS)"
    echo "  doctor            Run full health check on migration system"
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -v, --verbose    Show detailed output"
    echo ""
    echo "Examples:"
    echo "  ./migration_helper.sh check-models"
    echo "  ./migration_helper.sh diff"
    echo "  ./migration_helper.sh doctor"
    echo "  ./migration_helper.sh rollback"
    exit 0
}

# Parse arguments
COMMAND="$1"
VERBOSE=""

if [ -z "$COMMAND" ] || [ "$COMMAND" = "-h" ] || [ "$COMMAND" = "--help" ]; then
    show_help
fi

shift

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check models command
check_models() {
    echo "🔍 Checking eigen_models package..."
    echo "=================================="
    
    DATABASE_URL="$DATABASE_URL" python -c "
import sys
try:
    # Check package installation
    import eigen_models
    print('✅ eigen_models package found')
    print(f'   Package location: {eigen_models.__file__}')
    
    # Check version if available
    if hasattr(eigen_models, '__version__'):
        print(f'   Version: {eigen_models.__version__}')
    
    # Test Base import
    from eigen_models import Base
    print('✅ Successfully imported Base')
    
    # Count available tables
    table_count = len(Base.metadata.tables)
    print(f'   Tables defined: {table_count}')
    
    # Test key model imports
    key_models = [
        'User', 'TrackCase', 'MeetingInfo', 'Conversation', 
        'VaultFile', 'CnrProcessingQueue', 'Subscription'
    ]
    
    successful_imports = []
    failed_imports = []
    
    for model_name in key_models:
        try:
            model = getattr(eigen_models, model_name)
            successful_imports.append(model_name)
        except AttributeError:
            failed_imports.append(model_name)
    
    print(f'✅ Successfully imported models: {len(successful_imports)}/{len(key_models)}')
    if successful_imports:
        print(f'   Available: {\", \".join(successful_imports)}')
    
    if failed_imports:
        print(f'⚠️  Missing models: {\", \".join(failed_imports)}')
        print('   These models may not be exported in __init__.py')
    
    # Check for specific tables
    table_names = list(Base.metadata.tables.keys())
    print('\\n📋 Available Tables:')
    for table in sorted(table_names[:10]):  # Show first 10
        print(f'   - {table}')
    if len(table_names) > 10:
        print(f'   ... and {len(table_names) - 10} more')

except ImportError as e:
    print(f'❌ ImportError: {e}')
    print('\\n🔧 Solutions:')
    print('   1. Install the package: pip install git+https://github.com/eigen-ai/db-models.git')
    print('   2. Check if package is in requirements.txt')
    print('   3. Verify virtual environment is activated')
    sys.exit(1)
except Exception as e:
    print(f'❌ Unexpected error: {e}')
    sys.exit(1)
"
}

# Check database connection
check_connection() {
    echo "🔗 Checking database connection..."
    echo "================================="
    
    DATABASE_URL="$DATABASE_URL" python -c "
import os
import sys
from sqlalchemy import create_engine, text

try:
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL environment variable not set')
        print('\\n🔧 Set your database URL:')
        print('   export DATABASE_URL=\"postgresql://user:pass@localhost:5432/dbname\"')
        sys.exit(1)
    
    print(f'🔗 Connecting to database...')
    # Hide password in URL for display
    display_url = db_url.split('@')[0].split(':')[:-1]
    display_url = ':'.join(display_url) + ':****@' + db_url.split('@')[1]
    print(f'   URL: {display_url}')
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Test basic connection
        result = conn.execute(text('SELECT 1 as test'))
        print('✅ Basic connection successful')
        
        # Check database version
        try:
            version_result = conn.execute(text('SELECT version()'))
            version = version_result.scalar()
            print(f'   Database: {version.split()[0]} {version.split()[1]}')
        except:
            print('   Database version: Unknown')
        
        # Check if alembic_version table exists
        alembic_check = conn.execute(text(
            \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alembic_version')\"
        ))
        has_alembic = alembic_check.scalar()
        
        if has_alembic:
            print('✅ Alembic version table found')
            
            # Get current revision
            revision_result = conn.execute(text('SELECT version_num FROM alembic_version'))
            current_revision = revision_result.scalar()
            if current_revision:
                print(f'   Current revision: {current_revision}')
            else:
                print('   Current revision: None (empty database)')
        else:
            print('⚠️  Alembic version table not found - database not initialized')
            print('   Run: alembic upgrade head')

except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('\\n🔧 Troubleshooting:')
    print('   1. Check if database server is running')
    print('   2. Verify database credentials')
    print('   3. Ensure database exists')
    print('   4. Check network connectivity')
    sys.exit(1)
"
}

# Show model vs database differences
show_diff() {
    echo "🔍 Checking model vs database differences..."
    echo "==========================================="
    
    echo "Generating comparison (this may take a moment)..."
    cd migrations && alembic revision --autogenerate -m "temp_diff_check" --sql 2>/dev/null | head -50
    
    echo ""
    echo "💡 This shows what would change if you generated a migration now"
    echo "   If output is minimal, models and database are in sync"
}

# Show migration history  
show_history() {
    echo "📚 Migration History"
    echo "==================="
    
    cd migrations && alembic history $VERBOSE
    
    echo ""
    echo "📊 Summary:"
    TOTAL_MIGRATIONS=$(ls "$PROJECT_ROOT"/migrations/alembic/versions/*.py 2>/dev/null | wc -l)
    echo "   Total migrations: $TOTAL_MIGRATIONS"
    
    CURRENT_REVISION=$(cd "$PROJECT_ROOT/migrations" && alembic current 2>/dev/null | grep -v INFO | grep -v "Context impl" | grep -v "Will assume" | tail -n1 | awk '{print $1}')
    HEAD_REVISION=$(cd "$PROJECT_ROOT/migrations" && alembic heads 2>/dev/null | grep -v INFO | tail -n1 | awk '{print $1}')
    
    echo "   Current revision: $CURRENT_REVISION"
    echo "   Head revision: $HEAD_REVISION"
    
    if [ "$CURRENT_REVISION" = "$HEAD_REVISION" ]; then
        echo "   Status: ✅ Up to date"
    else
        echo "   Status: ⚠️  Migrations pending"
    fi
}

# Rollback to previous migration
rollback() {
    echo "⏪ Rolling back to previous migration..."
    echo "======================================"
    
    # Get current revision
    CURRENT=$(cd migrations && alembic current 2>/dev/null | grep -v INFO | grep -v "Context impl" | grep -v "Will assume" | tail -n1 | awk '{print $1}')
    
    if [ -z "$CURRENT" ]; then
        echo "❌ No current revision found"
        exit 1
    fi
    
    echo "Current revision: $CURRENT"
    
    # Get previous revision
    PREVIOUS=$(cd migrations && alembic history | grep -A1 "$CURRENT" | tail -n1 | awk '{print $1}' | sed 's/<-//')
    
    if [ -z "$PREVIOUS" ] || [ "$PREVIOUS" = "$CURRENT" ]; then
        echo "❌ No previous revision found"
        exit 1
    fi
    
    echo "Previous revision: $PREVIOUS"
    echo ""
    
    read -p "⚠️  Are you sure you want to rollback? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Rolling back..."
        cd migrations && alembic downgrade "$PREVIOUS" $VERBOSE
        
        if [ $? -eq 0 ]; then
            echo "✅ Rollback successful"
        else
            echo "❌ Rollback failed"
            exit 1
        fi
    else
        echo "Rollback cancelled"
    fi
}

# Reset database (dangerous)
reset_database() {
    echo "💀 DANGEROUS: Database Reset"
    echo "============================"
    echo ""
    echo "⚠️  This will:"
    echo "   1. Drop all tables"
    echo "   2. Remove all data"
    echo "   3. Reset migration state"
    echo "   4. Recreate from scratch"
    echo ""
    
    read -p "Are you ABSOLUTELY sure? Type 'RESET' to confirm: " -r
    
    if [ "$REPLY" = "RESET" ]; then
        echo ""
        echo "Resetting database..."
        
        # Drop all tables
        cd migrations && alembic downgrade base $VERBOSE
        
        # Recreate from scratch
        cd migrations && alembic upgrade head $VERBOSE
        
        if [ $? -eq 0 ]; then
            echo "✅ Database reset complete"
        else
            echo "❌ Reset failed"
            exit 1
        fi
    else
        echo "Reset cancelled"
    fi
}

# Run comprehensive health check
run_doctor() {
    echo "🏥 Migration System Health Check"
    echo "==============================="
    echo ""
    
    # Check 1: Models
    echo "1️⃣ Checking eigen_models package..."
    check_models
    echo ""
    
    # Check 2: Database connection
    echo "2️⃣ Checking database connection..."
    check_connection
    echo ""
    
    # Check 3: Migration state
    echo "3️⃣ Checking migration state..."
    ./migrations/scripts/validate_migration_state.sh
    echo ""
    
    # Check 4: Alembic configuration
    echo "4️⃣ Checking alembic configuration..."
    if [ -f "migrations/alembic.ini" ]; then
        echo "✅ alembic.ini found"
    else
        echo "❌ alembic.ini missing"
    fi
    
    if [ -f "migrations/alembic/env.py" ]; then
        echo "✅ alembic/env.py found"
        
            # Check if env.py imports eigen_models correctly
        if grep -q "from eigen_models import Base" migrations/alembic/env.py; then
            echo "✅ env.py imports eigen_models correctly"
        else
            echo "❌ env.py does not import eigen_models"
            echo "   Add: from eigen_models import Base"
        fi
    else
        echo "❌ alembic/env.py missing"
    fi
    echo ""
    
    # Check 5: Migration files
    echo "5️⃣ Checking migration files..."
    MIGRATION_COUNT=$(ls migrations/alembic/versions/*.py 2>/dev/null | wc -l)
    echo "   Migration files: $MIGRATION_COUNT"
    
    if [ $MIGRATION_COUNT -gt 0 ]; then
        echo "✅ Migration files found"
        
        # Check for common issues
        BROKEN_MIGRATIONS=$(grep -l "pass" migrations/alembic/versions/*.py 2>/dev/null | wc -l)
        if [ $BROKEN_MIGRATIONS -gt 0 ]; then
            echo "⚠️  Found $BROKEN_MIGRATIONS migrations with 'pass' (likely empty)"
        fi
    else
        echo "⚠️  No migration files found"
    fi
    echo ""
    
    echo "🏁 Health check complete!"
}

# Execute command
case $COMMAND in
    check-models)
        check_models
        ;;
    check-connection)
        check_connection
        ;;
    diff)
        show_diff
        ;;
    history)
        show_history
        ;;
    rollback)
        rollback
        ;;
    reset)
        reset_database
        ;;
    doctor)
        run_doctor
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        ;;
esac