"""
Скрипт для генерации SQL DDL из ORM-моделей SQLAlchemy.

Полученный файл schema.sql можно использовать для:
    - Автоматического построения ER-диаграмм (dbdiagram.io, QuickDBD, DBeaver)
    - Документирования структуры базы данных
    - Миграции на другую СУБД

Использование:
    python generate_schema.py
"""
from app import app
from extensions import db
from models import User, Item, Reservation, ReadHistory
from sqlalchemy.schema import CreateTable


def generate_schema():
    """Генерирует SQL DDL для всех моделей"""
    with app.app_context():
        output = []
        output.append("-- Схема базы данных 'Моя библиотека'")
        output.append("-- Сгенерировано автоматически из SQLAlchemy ORM-моделей\n")

        # Генерируем CREATE TABLE для каждой модели
        for model in [User, Item, Reservation, ReadHistory]:
            table = model.__table__
            create_stmt = str(CreateTable(table).compile(db.engine))
            output.append(f"-- Таблица: {table.name}")
            output.append(f"-- Описание: {model.__doc__ or ''}")
            output.append(create_stmt)
            output.append("")

        # Добавляем комментарии к связям
        output.append("\n-- === СВЯЗИ МЕЖДУ ТАБЛИЦАМИ ===")
        output.append("--")
        output.append("-- users 1:N reservations     (пользователь бронирует элементы)")
        output.append("-- users 1:N read_history     (пользователь читает книги)")
        output.append("-- users 1:N items            (пользователь предлагает книги)")
        output.append("-- items 1:N reservations     (элемент бронируется пользователями)")
        output.append("-- items 1:N read_history     (книга читается пользователями)")

        schema = "\n".join(output)

        # Записываем в файл
        with open("schema.sql", "w", encoding="utf-8") as f:
            f.write(schema)

        print("Схема успешно сгенерирована в файл schema.sql")
        print("\n--- Предпросмотр ---\n")
        print(schema)


if __name__ == "__main__":
    generate_schema()
