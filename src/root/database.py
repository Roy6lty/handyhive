import os
import shutil
from sqlalchemy import MetaData, create_engine, inspect
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from alembic.config import Config
from src.root.env_settings import env
from src.database.orms.user_orm import AbstractBase
from alembic import command
from alembic.util.exc import CommandError

async_database_connection_url = str(env.POSTGRES_URL)


# Async
engine = create_async_engine(async_database_connection_url)


SessionLocal = async_sessionmaker(engine)

# Base = declarative_base()


async def startup():
    async with engine.begin() as conn:
        if env.DEBUG_MODE:
            print("--staring database---")
        await conn.run_sync(AbstractBase.metadata.create_all)


async def shutdown():
    if env.DEBUG_MODE:
        print("--shutting down database--")
    await engine.dispose()


# database dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


db_dependency = Annotated[AsyncSession, Depends(get_db)]


def create_migration():
    if env.DB_MIGRATION_ENV:
        # Initialize Alembic configuration

        alembic_ini_path = "db_migrations.ini"
        alembic_config = Config(alembic_ini_path)

        metadata = MetaData()
        postgres_url = env.POSTGRES_URL.split("//")

        metadata.reflect(
            bind=create_engine(
                url=f"postgresql://{postgres_url[-1]}",
            )
        )

        existing_tables = set(metadata.tables.keys())
        defined_tables = set(AbstractBase.metadata.tables.keys())

        changed_columns = []
        table_names = []
        removed_columns = set()
        new_table = list(defined_tables - existing_tables)

        message = "_".join(new_table)
        if list(defined_tables - existing_tables):
            try:
                # Generate migration script
                script = command.revision(
                    config=alembic_config, autogenerate=True, message=message
                )
                command.upgrade(alembic_config, "head")
            except CommandError as e:
                raise e

            except Exception as e:
                if not script:
                    raise e
                else:
                    move_failed_migration(script)

        else:

            for table_name, table in AbstractBase.metadata.tables.items():
                existing_columns = {
                    c.name: c for c in inspect(metadata.tables[table_name]).c
                }
                defined_columns = {c.name: c for c in table.c}
                removed_columns.update(
                    set(existing_columns.keys()) - set(defined_columns.keys())
                )
                print(removed_columns)

                # Check for changes in columns
                for column_name, column in defined_columns.items():
                    if column_name not in existing_columns or not isinstance(
                        existing_columns[column_name].type, type(column.type)
                    ):
                        table_names.append(table_name)
                        changed_columns.append(column_name)
                        print(changed_columns)

        if changed_columns or removed_columns:
            message = (
                f"Columns changed in table { '_'.join(table_names)}:"
                f" {', '.join(changed_columns)}"
            )

            # Generate migration script
            try:

                # Generate migration script
                script = command.revision(
                    config=alembic_config, autogenerate=True, message=message
                )

                command.upgrade(alembic_config, "head")
            except CommandError as e:
                raise e
            except Exception as e:
                if not script:
                    raise e
                else:
                    move_failed_migration(script)

        else:
            print("No new changes found.")


def move_failed_migration(scripts):
    failed_dir = "failed_migrations"
    os.makedirs(failed_dir, exist_ok=True)

    if isinstance(scripts, list):
        for script in scripts:
            shutil.move(script, os.path.join(failed_dir, os.path.basename(script.path)))
    else:
        shutil.move(
            scripts.path, os.path.join(failed_dir, os.path.basename(scripts.path))
        )

    print(f"Moved failed migration script to {failed_dir}")
