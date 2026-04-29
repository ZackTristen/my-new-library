# models.py
"""
ORM-модели базы данных приложения "Моя библиотека".

Таблицы:
    - users: Пользователи системы (студенты, администраторы)
    - items: Элементы каталога (книги, фильмы и т.д.)
    - reservations: Бронирования элементов пользователями
    - read_history: История прочтений пользователей

Связи:
    - User 1:N Reservation  (пользователь может бронировать много элементов)
    - User 1:N ReadHistory  (пользователь может читать много книг)
    - User 1:N Item         (пользователь может предлагать новые книги)
    - Item 1:N Reservation  (элемент может быть забронирован много раз)
    - Item 1:N ReadHistory  (книга может быть прочитана много раз)
"""
from extensions import db
from datetime import datetime


class User(db.Model):
    """Таблица пользователей."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='Уникальный идентификатор пользователя')
    username = db.Column(db.String(80), unique=True, nullable=False, comment='Имя пользователя (логин)')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='Электронная почта')
    password_hash = db.Column(db.String(256), nullable=False, comment='Хеш пароля')
    last_name = db.Column(db.String(120), comment='Фамилия')
    patronymic = db.Column(db.String(120), comment='Отчество')
    group_number = db.Column(db.String(50), comment='Номер учебной группы')
    role = db.Column(db.String(20), nullable=False, default='user', comment='Роль: user или admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='Дата регистрации')
    last_login = db.Column(db.DateTime, comment='Дата последнего входа')
    is_active = db.Column(db.Boolean, default=True, comment='Флаг активности аккаунта')

    # Связи
    reservations = db.relationship('Reservation', back_populates='user', lazy=True, cascade='all, delete-orphan')
    suggested_items = db.relationship('Item', back_populates='suggester', lazy=True)
    read_history = db.relationship('ReadHistory', back_populates='user', lazy=True, cascade='all, delete-orphan')

    # Flask-Login методы
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'


class Item(db.Model):
    """Таблица элементов каталога (книги, фильмы и т.д.)."""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='Уникальный идентификатор элемента')
    title = db.Column(db.String(200), nullable=False, comment='Название')
    author = db.Column(db.String(200), comment='Автор')
    type = db.Column(db.String(50), comment='Тип: Книга, Фильм и т.д.')
    genre = db.Column(db.String(100), comment='Жанр')
    status = db.Column(db.String(50), default='Доступна', comment='Статус: Доступна, Забронирована, На рассмотрении')
    image_url = db.Column(db.String(500), comment='URL обложки')
    description = db.Column(db.Text, comment='Описание')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='Дата добавления')
    suggested_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='ID пользователя, предложившего элемент')

    # Связи
    suggester = db.relationship('User', back_populates='suggested_items')
    reservations = db.relationship('Reservation', back_populates='item', lazy=True, cascade='all, delete-orphan')
    read_history = db.relationship('ReadHistory', back_populates='item', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Item {self.title}>'


class Reservation(db.Model):
    """Таблица бронирований элементов пользователями."""
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='Уникальный идентификатор бронирования')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='ID забронированного элемента')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='ID забронировавшего пользователя')
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow, comment='Дата бронирования')
    status = db.Column(db.String(20), default='active', comment='Статус: active, completed, cancelled')
    expires_at = db.Column(db.DateTime, comment='Дата окончания срока бронирования')

    # Связи
    user = db.relationship('User', back_populates='reservations')
    item = db.relationship('Item', back_populates='reservations')

    def __repr__(self):
        return f'<Reservation {self.id}>'


class ReadHistory(db.Model):
    """Таблица истории прочтений пользователей."""
    __tablename__ = 'read_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='Уникальный идентификатор записи')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='ID пользователя')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='ID прочитанного элемента')
    read_at = db.Column(db.DateTime, default=datetime.utcnow, comment='Дата прочтения')

    # Связи
    user = db.relationship('User', back_populates='read_history')
    item = db.relationship('Item', back_populates='read_history')

    def __repr__(self):
        return f'<ReadHistory user={self.user_id} item={self.item_id}>'
