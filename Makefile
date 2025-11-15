# Makefile for Eigen Models - Database Migration Management
# Simple delegation to migration scripts

.PHONY: help migrate migrate-dry generate status history rollback validate doctor reset clean

# Default target - show help
help:
	@echo "Eigen Models - Database Migration Management"
	@echo "==========================================="
	@echo ""
	@echo "Environment Selection (default: dev):"
	@echo "  Add ENV=prod to any command to use production environment"
	@echo "  Example: make migrate ENV=prod"
	@echo ""
	@echo "Quick Commands:"
	@echo "  make status            Check current migration status"
	@echo "  make migrate           Apply pending migrations"
	@echo "  make migrate-dry       Preview migrations (dry run)"
	@echo "  make generate name=... Generate new migration"
	@echo ""
	@echo "Management Commands:"
	@echo "  make history           Show migration history"
	@echo "  make validate          Validate models and DB connection"
	@echo "  make doctor            Run comprehensive health check"
	@echo "  make rollback          Rollback to previous migration"
	@echo "  make reset             Reset database (DANGEROUS)"
	@echo ""
	@echo "Examples:"
	@echo "  make status                      # Check dev database status"
	@echo "  make status ENV=prod             # Check prod database status"
	@echo "  make migrate                     # Apply migrations to dev"
	@echo "  make migrate ENV=prod            # Apply migrations to prod"
	@echo "  make generate name=\"add_table\"  # Generate migration using dev"
	@echo ""

# Check current migration status
status:
	@ENV=$(ENV) ./migrations/scripts/validate_migration_state.sh

# Apply pending migrations
migrate:
	@ENV=$(ENV) ./migrations/scripts/apply_migrations.sh

# Preview migrations without applying (dry run)
migrate-dry:
	@ENV=$(ENV) ./migrations/scripts/apply_migrations.sh --dry-run

# Generate a new migration
generate:
	@if [ -z "$(name)" ]; then \
		echo "Error: Please provide a migration name"; \
		echo "Usage: make generate name=\"your_migration_name\""; \
		exit 1; \
	fi
	@ENV=$(ENV) ./migrations/scripts/generate_migration.sh "$(name)"

# Show migration history
history:
	@ENV=$(ENV) ./migrations/scripts/migration_helper.sh history

# Validate models and database connection
validate:
	@ENV=$(ENV) ./migrations/scripts/migration_helper.sh check-models
	@ENV=$(ENV) ./migrations/scripts/migration_helper.sh check-connection

# Run comprehensive health check
doctor:
	@ENV=$(ENV) ./migrations/scripts/migration_helper.sh doctor

# Rollback to previous migration
rollback:
	@ENV=$(ENV) ./migrations/scripts/migration_helper.sh rollback

# Reset database - DANGEROUS!
reset:
	@ENV=$(ENV) ./migrations/scripts/migration_helper.sh reset

# Clean up Python cache files
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"