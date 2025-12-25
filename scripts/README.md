# Database Migration Scripts

## UUIDv7 Migration for Group Messages

### Overview
This migration adds `public_id` (UUIDv7) to `group_messages` table and `last_seen_public_id` to `project_group_members` table for cursor-based message sync.

### Migration Steps

**Step 1: Run Phase 1 Alembic Migration**
```bash
cd db_models
alembic upgrade f2a3b4c5d6e7
```
This adds the nullable `public_id` column.

**Step 2: Run Data Migration Script**
```bash
# Set your database URL
export DATABASE_URL=postgresql://user:password@localhost:5432/eigen

# Dry run first (recommended)
python scripts/migrate_public_ids_to_uuidv7.py --dry-run

# Run the actual migration
python scripts/migrate_public_ids_to_uuidv7.py
```

**Step 3: Run Phase 2 Alembic Migration**
```bash
alembic upgrade g3b4c5d6e7f8
```
This makes `public_id` non-nullable and adds indexes.

### Script Options

```bash
python scripts/migrate_public_ids_to_uuidv7.py --help

Options:
  --batch-size  Number of records to update per batch (default: 1000)
  --dry-run     Show what would be done without making changes
```

### Rollback

To rollback:
```bash
# Rollback Phase 2
alembic downgrade f2a3b4c5d6e7

# Rollback Phase 1
alembic downgrade e1f2a3b4c5d6
```

### Requirements

The data migration script requires:
- `psycopg2` (PostgreSQL adapter)

Install with:
```bash
pip install psycopg2-binary
```
