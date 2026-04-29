# database.py
from extensions import db


def init_db(app):
    """Инициализация базы данных через SQLAlchemy"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
