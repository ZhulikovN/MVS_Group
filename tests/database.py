# pylint: disable=invalid-name
import logging

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    text,
)
from sqlalchemy.engine import Engine

from src.settings import settings


class DBTest:

    def __init__(self, db_name: str) -> None:
        self.NEW_DB_NAME = db_name

    def engine(self, database: str = "image_app") -> Engine:
        db_url = (
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{database}"
        )
        engine = create_engine(db_url, isolation_level="AUTOCOMMIT", echo=True)
        return engine

    def create_database(self) -> None:
        try:
            engine = self.engine()
            with engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname='{self.NEW_DB_NAME}'")
                )
                db_exists = result.fetchone()
                if not db_exists:
                    conn.execute(text(f"CREATE DATABASE {self.NEW_DB_NAME}"))
                    print("База данных успешно создана")
                else:
                    print(f"База данных {self.NEW_DB_NAME} уже существует.")
        except Exception as e:
            logging.error(f"Произошла ошибка при создании базы данных: {e}", exc_info=True)

    def drop_database(self) -> None:
        try:
            engine = self.engine()
            with engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.NEW_DB_NAME}"))
                print("База данных успешно удалена")
        except Exception as e:
            logging.error(f"Произошла ошибка при удалении базы данных: {e}", exc_info=True)

    def create_table(self) -> None:
        try:
            engine = self.engine(database=self.NEW_DB_NAME)
            metadata = MetaData()

            model_test = Table(
                "images",
                metadata,
                Column("id", Integer, primary_key=True),
                Column("description", String(200), nullable=False),
                Column("timestamp", DateTime(timezone=True), server_default=func.now()),
                Column("image_path", String, nullable=True),
                extend_existing=True,
            )
            metadata.create_all(engine, tables=[model_test])
            print("Таблица успешно создана")
        except Exception as e:
            logging.error(f"Произошла ошибка при создании таблицы: {e}", exc_info=True)

    def setup_database(self) -> None:
        self.create_database()
        self.create_table()
