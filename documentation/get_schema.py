import sqlite3
import os

DB_FILE = 'my_library.db'

if not os.path.exists(DB_FILE):
    print(f"Ошибка: Файл базы данных '{DB_FILE}' не найден.")
    exit()

try:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema_rows = c.fetchall()
    conn.close()

    if not schema_rows:
        print(f"В базе данных '{DB_FILE}' не найдено таблиц.")
    else:
        for row in schema_rows:
            if row[0]:
                print(row[0] + ";") # Add semicolon for clarity
except Exception as e:
    print(f"Произошла ошибка при чтении схемы: {e}")
