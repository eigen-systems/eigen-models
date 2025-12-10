import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Determine which environment file to load based on ENV variable
env_name = os.environ.get('ENV', 'dev')  # Default to 'dev'
if env_name == 'prod':
    env_file = '../.env.prod'
else:
    env_file = '../.env.dev'

# Try to load the environment-specific file first
# The path is relative to the migrations directory where alembic runs
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    # Fall back to .env for backwards compatibility
    # Check both in migrations dir and parent dir
    if os.path.exists('../.env'):
        load_dotenv('../.env')
    else:
        load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# set up the alchemy sql url
database_url = os.environ.get("DATABASE_URL")
# SQLAlchemy 2.0+ requires postgresql:// instead of postgres://
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Add project root to Python path to ensure eigen_models can be imported
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from eigen_models import Base
# Import geoalchemy2 to ensure it's available during migration generation
import geoalchemy2  # noqa: F401

target_metadata = Base.metadata

# PostGIS system tables that should be excluded from migrations
POSTGIS_SYSTEM_TABLES = {
    'spatial_ref_sys',
    'geography_columns',
    'geometry_columns',
    'raster_columns',
    'raster_overviews',
}


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter function to exclude PostGIS system tables from autogenerate.
    
    This prevents Alembic from trying to drop or modify PostGIS system tables
    which are managed by the PostGIS extension and should not be touched.
    
    Args:
        object: The object being considered
        name: Name of the object
        type_: Type of object ('table', 'column', 'index', etc.)
        reflected: Whether the object was reflected from the database
        compare_to: The object being compared against
    
    Returns:
        bool: True to include the object, False to exclude it
    """
    # Exclude PostGIS system tables
    if type_ == 'table' and name in POSTGIS_SYSTEM_TABLES:
        return False
    
    # Include all other objects
    return True


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
