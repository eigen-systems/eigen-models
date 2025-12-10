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
# Handle --prod flag if it's the first argument
if [ "$ENV" = "prod" ]; then
    ENV_FILE=".env.prod"
    ENV_NAME="prod"
elif [ "$1" = "--prod" ]; then
    ENV_FILE=".env.prod"
    ENV_NAME="prod"
    shift  # Remove --prod from arguments
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
    echo "Usage: ./generate_migration.sh [--prod] <migration_name> [options]"
    echo ""
    echo "Arguments:"
    echo "  migration_name    Name for the migration (required)"
    echo ""
    echo "Options:"
    echo "  --prod           Use production environment (.env.prod)"
    echo "  -h, --help       Show this help message"
    echo "  -v, --verbose    Show detailed output"
    echo "  --dry-run        Show what would be generated without creating"
    echo "  --validate       Validate model imports before generation"
    echo ""
    echo "Environment:"
    echo "  Default: Uses .env.dev (or set ENV=prod environment variable)"
    echo ""
    echo "Examples:"
    echo "  ./generate_migration.sh add_user_table"
    echo "  ./generate_migration.sh --prod add_user_table"
    echo "  ./generate_migration.sh \"Add new user fields\" --validate"
    exit 0
}

# Check if a migration name was provided
if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
fi

# Get migration name (first argument after any flags)
MIGRATION_NAME="$1"
shift

# Parse command line arguments
DRY_RUN=false
VERBOSE=""
VALIDATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --validate)
            VALIDATE=true
            shift
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
    
    # Test specific model imports
    from eigen_models import User, GitHubAccount, Profile, Post
    print('✅ Successfully imported core models')
    print(f'   Models: User, GitHubAccount, Profile, Post')
    
except ImportError as e:
    print(f'❌ Import Error: {e}')
    print('   Make sure eigen_models package is installed:')
    print('   pip install git+https://github.com/eigen-systems/eigen-models.git')
    exit(1)
except Exception as e:
    print(f'❌ Unexpected Error: {e}')  
    exit(1)
" || exit 1
    echo ""
fi

# Sanitize the migration name
# Convert to lowercase, replace spaces with underscores, remove special characters
SANITIZED_NAME=$(echo "$MIGRATION_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | sed 's/[^a-z0-9_]//g')

echo "📝 Migration Details:"
echo "   Original name: $MIGRATION_NAME"
echo "   Sanitized name: $SANITIZED_NAME"
echo ""

# Check current migration state first
echo "🔍 Checking current migration state..."
./migrations/scripts/validate_migration_state.sh
if [ $? -ne 0 ]; then
    echo "❌ Migration state validation failed"
    echo "   Please resolve migration state issues before creating new migrations"
    exit 1
fi
echo ""

# If dry run, show what would be generated
if [ "$DRY_RUN" = true ]; then
    echo "🔍 Dry run - checking for model changes without creating migration file:"
    echo "   Note: No migration file will be created in dry-run mode"
    echo "   This validates model imports and database connectivity only"
    
    # Test database connection and current state
    CURRENT_HEAD=$(cd migrations && alembic current 2>/dev/null | grep -v "INFO" | head -n1)
    if [ -n "$CURRENT_HEAD" ]; then
        echo "✅ Database connection successful"
        echo "   Current migration: $CURRENT_HEAD"
    else
        echo "❌ Database connection failed"
        exit 1
    fi
    
    echo "✅ Dry run completed - ready to generate migration"
    exit 0
fi

# Ensure versions directory exists
VERSIONS_DIR="migrations/alembic/versions"
if [ ! -d "$VERSIONS_DIR" ]; then
    echo "📁 Creating versions directory..."
    mkdir -p "$VERSIONS_DIR"
    # Create __init__.py if it doesn't exist (for Python package)
    touch "$VERSIONS_DIR/__init__.py"
    echo "✅ Versions directory created"
fi

# Generate timestamp for logging
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create the migration
echo "📦 Generating migration..."
echo "   Name: ${SANITIZED_NAME}"
echo "   Time: ${TIMESTAMP}"
echo ""

cd migrations && alembic revision --autogenerate -m "${SANITIZED_NAME}" $VERBOSE

# Check if the migration was created successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration created successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Review the generated migration file in migrations/alembic/versions/"
    echo "   2. Test the migration: ./migrations/scripts/apply_migrations.sh --dry-run"
    echo "   3. Apply the migration: ./migrations/scripts/apply_migrations.sh"
    echo "   4. Validate state: ./migrations/scripts/validate_migration_state.sh"
    echo ""
    
    # Show the generated migration file
    LATEST_MIGRATION=$(ls -t migrations/alembic/versions/*.py | head -n1)
    if [ -f "$LATEST_MIGRATION" ]; then
        echo "📁 Generated file: $LATEST_MIGRATION"
        echo "   File size: $(wc -l < "$LATEST_MIGRATION") lines"
    fi
else
    echo ""
    echo "❌ Error: Failed to create migration"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check database connection: make status"
    echo "   2. Validate model imports: ./migrations/scripts/generate_migration.sh dummy --validate"
    echo "   3. Check migration state: make status"
    exit 1
fi 