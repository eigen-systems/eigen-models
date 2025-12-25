#!/usr/bin/env python3
"""
Data Migration Script: Generate UUIDv7 for existing group messages.

This script converts existing group_messages.public_id values to proper UUIDv7
based on the created_at timestamp to preserve chronological ordering.

UUIDv7 Format:
- Bits 0-47: Unix timestamp in milliseconds
- Bits 48-51: Version (7)
- Bits 52-63: Random
- Bits 64-65: Variant (10)
- Bits 66-127: Random

Usage:
    python migrate_public_ids_to_uuidv7.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string

Example:
    DATABASE_URL=postgresql://user:pass@localhost:5432/eigen python migrate_public_ids_to_uuidv7.py
"""

import os
import sys
import time
import secrets
from datetime import datetime
from uuid import UUID
from typing import Optional

import psycopg2
from psycopg2.extras import execute_batch


def timestamp_to_uuidv7(dt: datetime, counter: int = 0) -> UUID:
    """
    Generate a UUIDv7 from a datetime object.

    Args:
        dt: The datetime to use for the timestamp portion
        counter: Optional counter to ensure uniqueness for same-millisecond messages

    Returns:
        A UUID object containing the UUIDv7
    """
    # Get timestamp in milliseconds
    timestamp_ms = int(dt.timestamp() * 1000)

    # Add counter to ensure uniqueness for same-millisecond messages
    # This shifts by a small amount while staying within the same second
    timestamp_ms += counter % 1000

    # Generate random bits for the rest
    rand_bytes = secrets.token_bytes(10)

    # Build the UUID bytes
    # Bytes 0-5: timestamp (48 bits)
    uuid_bytes = timestamp_ms.to_bytes(6, byteorder='big')

    # Bytes 6-7: version (4 bits) + random (12 bits)
    # Version 7 = 0111
    rand_a = int.from_bytes(rand_bytes[0:2], byteorder='big')
    rand_a = (rand_a & 0x0FFF) | 0x7000  # Set version to 7
    uuid_bytes += rand_a.to_bytes(2, byteorder='big')

    # Bytes 8-15: variant (2 bits) + random (62 bits)
    # Variant = 10
    rand_b = int.from_bytes(rand_bytes[2:10], byteorder='big')
    rand_b = (rand_b & 0x3FFFFFFFFFFFFFFF) | 0x8000000000000000  # Set variant to 10
    uuid_bytes += rand_b.to_bytes(8, byteorder='big')

    return UUID(bytes=uuid_bytes)


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("ERROR: DATABASE_URL environment variable is required")
        print("Example: DATABASE_URL=postgresql://user:pass@localhost:5432/eigen")
        sys.exit(1)
    return url


def migrate_public_ids(batch_size: int = 1000, dry_run: bool = False):
    """
    Migrate existing group_messages.public_id to proper UUIDv7.

    Args:
        batch_size: Number of records to update per batch
        dry_run: If True, don't actually update, just print what would be done
    """
    db_url = get_database_url()

    print(f"Connecting to database...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # Count total messages
            cur.execute("SELECT COUNT(*) FROM group_messages")
            total_count = cur.fetchone()[0]
            print(f"Total messages to migrate: {total_count}")

            if total_count == 0:
                print("No messages to migrate.")
                return

            # Fetch all messages ordered by created_at
            print("Fetching messages ordered by created_at...")
            cur.execute("""
                SELECT id, created_at
                FROM group_messages
                ORDER BY created_at ASC, id ASC
            """)

            messages = cur.fetchall()
            print(f"Fetched {len(messages)} messages")

            # Generate UUIDv7 for each message
            updates = []
            last_timestamp = None
            counter = 0

            for msg_id, created_at in messages:
                # Track counter for same-millisecond messages
                if last_timestamp and created_at == last_timestamp:
                    counter += 1
                else:
                    counter = 0
                    last_timestamp = created_at

                # Generate UUIDv7 based on created_at
                new_public_id = timestamp_to_uuidv7(created_at, counter)
                updates.append((str(new_public_id), msg_id))

            print(f"Generated {len(updates)} UUIDv7 values")

            if dry_run:
                print("\n[DRY RUN] Would update the following:")
                for public_id, msg_id in updates[:10]:
                    print(f"  Message {msg_id}: {public_id}")
                if len(updates) > 10:
                    print(f"  ... and {len(updates) - 10} more")
                return

            # Update in batches
            print(f"Updating messages in batches of {batch_size}...")
            start_time = time.time()

            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                execute_batch(
                    cur,
                    "UPDATE group_messages SET public_id = %s WHERE id = %s",
                    batch,
                    page_size=batch_size
                )

                progress = min(i + batch_size, len(updates))
                elapsed = time.time() - start_time
                rate = progress / elapsed if elapsed > 0 else 0
                print(f"  Updated {progress}/{len(updates)} ({progress * 100 / len(updates):.1f}%) - {rate:.0f} msgs/sec")

            # Commit the transaction
            conn.commit()

            elapsed = time.time() - start_time
            print(f"\nMigration completed successfully!")
            print(f"  Total messages updated: {len(updates)}")
            print(f"  Total time: {elapsed:.2f} seconds")
            print(f"  Average rate: {len(updates) / elapsed:.0f} messages/second")

            # Verify the migration
            print("\nVerifying migration...")
            cur.execute("""
                SELECT COUNT(*) FROM group_messages WHERE public_id IS NULL
            """)
            null_count = cur.fetchone()[0]
            if null_count > 0:
                print(f"WARNING: {null_count} messages still have NULL public_id")
            else:
                print("All messages have valid public_id values")

            # Verify chronological ordering
            print("Verifying chronological ordering...")
            cur.execute("""
                SELECT COUNT(*) FROM (
                    SELECT id, created_at, public_id,
                           LAG(public_id) OVER (ORDER BY created_at, id) as prev_public_id
                    FROM group_messages
                ) sub
                WHERE prev_public_id IS NOT NULL
                  AND public_id::text < prev_public_id::text
            """)
            out_of_order = cur.fetchone()[0]
            if out_of_order > 0:
                print(f"WARNING: {out_of_order} messages may be out of order")
            else:
                print("All messages are in chronological order by public_id")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: Migration failed: {e}")
        raise
    finally:
        conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate group_messages.public_id to proper UUIDv7"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records to update per batch (default: 1000)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("UUIDv7 Data Migration for group_messages.public_id")
    print("=" * 60)
    print()

    if args.dry_run:
        print(">>> DRY RUN MODE - No changes will be made <<<")
        print()

    migrate_public_ids(batch_size=args.batch_size, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
