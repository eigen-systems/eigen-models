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

# Function to display help message
show_help() {
    echo "Usage: ./apply_migrations.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -d, --dry-run       Show what would be applied without actually applying"
    echo "  -v, --verbose       Show detailed output"
    echo "  --validate          Validate model imports and state before applying"
    echo "  --backup            Create database backup before applying (requires pg_dump)"
    echo "  --target REVISION   Upgrade/downgrade to specific revision"
    echo ""
    echo "Examples:"
    echo "  ./apply_migrations.sh                    # Apply all pending migrations"
    echo "  ./apply_migrations.sh --dry-run          # Show what would be applied"
    echo "  ./apply_migrations.sh --validate --backup # Full safety checks"
    echo "  ./apply_migrations.sh --target abc123    # Migrate to specific revision"
    exit 0
}

# Parse command line arguments
DRY_RUN=false
VERBOSE=""
VALIDATE=false
BACKUP=false
TARGET_REVISION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --validate)
            VALIDATE=true
            shift
            ;;
        --backup)
            BACKUP=true
            shift
            ;;
        --target)
            TARGET_REVISION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Validate model imports if requested
if [ "$VALIDATE" = true ]; then
    echo "🔍 Validating eigen_models imports..."
    DATABASE_URL="$DATABASE_URL" python -c "
try:
    from eigen_models import Base
    print('✅ Successfully imported Base from eigen_models')
    print(f'   Metadata tables: {len(Base.metadata.tables)} tables found')
    
    # Test database connection
    import os
    from sqlalchemy import create_engine, text
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL environment variable not set')
        exit(1)
    
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
    
except ImportError as e:
    print(f'❌ Import Error: {e}')
    print('   Make sure eigen_models package is installed')
    exit(1)
except Exception as e:
    print(f'❌ Connection Error: {e}')
    exit(1)
" || exit 1
    echo ""
fi

# Create backup if requested
if [ "$BACKUP" = true ]; then
    echo "💾 Creating database backup..."
    
    # Check if pg_dump is available
    if ! command -v pg_dump &> /dev/null; then
        echo "❌ pg_dump not found. Install PostgreSQL client tools to use --backup option"
        exit 1
    fi
    
    # Extract database info from DATABASE_URL
    DB_URL="${DATABASE_URL}"
    if [ -z "$DB_URL" ]; then
        echo "❌ DATABASE_URL environment variable not set"
        exit 1
    fi
    
    # Generate backup filename with timestamp
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    echo "   Creating backup: $BACKUP_FILE"
    pg_dump "$DB_URL" > "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ Backup created successfully: $BACKUP_FILE"
        echo "   Size: $(du -h "$BACKUP_FILE" | cut -f1)"
    else
        echo "❌ Backup failed"
        exit 1
    fi
    echo ""
fi

# Show current migration status
echo "📊 Current migration status:"
CURRENT_REVISION=$(cd migrations && alembic current 2>/dev/null | grep -v INFO | grep -v "Context impl" | grep -v "Will assume" | tail -n1 | awk '{print $1}')
HEAD_REVISION=$(cd migrations && alembic heads 2>/dev/null | grep -v INFO | tail -n1 | awk '{print $1}')

echo "   Database: $CURRENT_REVISION"
echo "   Latest:   $HEAD_REVISION"

if [ "$CURRENT_REVISION" = "$HEAD_REVISION" ]; then
    if [ -z "$TARGET_REVISION" ]; then
        echo "✅ Database is up to date - no migrations needed"
        exit 0
    fi
else
    echo "📋 Pending migrations detected"
fi
echo ""

# Determine target for migration
if [ -n "$TARGET_REVISION" ]; then
    MIGRATION_TARGET="$TARGET_REVISION"
    echo "🎯 Target revision: $TARGET_REVISION"
else
    MIGRATION_TARGET="head"
    echo "🎯 Target: head (latest)"
fi
echo ""

# If dry run, show what would be applied
if [ "$DRY_RUN" = true ]; then
    echo "🔍 Dry run - showing what would be applied:"
    echo "=========================================="
    cd migrations && alembic upgrade "$MIGRATION_TARGET" --sql
    echo "=========================================="
    echo ""
    echo "💡 To apply these migrations, run without --dry-run flag"
    exit 0
fi

# Apply migrations
echo "⚡ Applying migrations..."
echo "   Target: $MIGRATION_TARGET"
echo "   Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run the migration
if [ -n "$VERBOSE" ]; then
    echo "🔧 Running migration with detailed output..."
    cd migrations && alembic upgrade "$MIGRATION_TARGET"
else
    cd migrations && alembic upgrade "$MIGRATION_TARGET"
fi

# Check if the migration was applied successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations applied successfully!"
    
    # Show final state
    echo ""
    echo "📊 Final migration status:"
    ./migrations/scripts/validate_migration_state.sh
    
    # Cleanup old backups (keep last 5)
    if [ "$BACKUP" = true ]; then
        echo ""
        echo "🧹 Cleaning up old backups (keeping last 5)..."
        ls -t backup_*.sql 2>/dev/null | tail -n +6 | xargs -r rm
        echo "   Remaining backups: $(ls backup_*.sql 2>/dev/null | wc -l)"
    fi
    
else
    echo ""
    echo "❌ Error: Failed to apply migrations"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check database connection and permissions"
    echo "   2. Review migration file for syntax errors"
    echo "   3. Check database logs for detailed error messages"
    echo "   4. Consider rolling back to previous state if needed"
    
    if [ "$BACKUP" = true ] && [ -f "$BACKUP_FILE" ]; then
        echo "   5. Restore from backup if needed: psql \$DATABASE_URL < $BACKUP_FILE"
    fi
    
    exit 1
fi 