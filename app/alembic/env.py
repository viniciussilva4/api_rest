from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

from alembic import context

from dotenv import load_dotenv
import os

from presentation.viewmodels.models import Clients, Users, Products, Orders, OrderProductLink

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
PREFIX = os.getenv('PREFIX')

DATABASE_URL = f'{PREFIX}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

config = context.config
fileConfig(config.config_file_name)

if config.config_file_name is not None:

    fileConfig(config.config_file_name)

config.set_main_option('sqlalchemy.url', DATABASE_URL)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},)

    with context.begin_transaction():

        context.run_migrations()


def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix = "sqlalchemy.",
        poolclass=pool.NullPool,)

    with connectable.connect() as connection:

        context.configure(connection = connection, target_metadata = target_metadata)

        with context.begin_transaction():

            context.run_migrations()


if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()