import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData
from sqlalchemy import engine_from_config, pool

# This line creates an empty MetaData object
target_metadata = MetaData()

# Configure Alembic logging
config_path = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')
fileConfig(config_path)

# Database connection configuration
config = context.config
config.set_main_option('sqlalchemy.url', os.getenv('DB_URL'))


# This function is called when Alembic needs to generate a new revision
def run_migrations_offline():
    context.configure(
        url=config.get_main_option('sqlalchemy.url'),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# This function is called when Alembic needs to generate a new revision with online database support
def run_migrations_online():
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


# Call the appropriate function based on the context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
