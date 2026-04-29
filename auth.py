# auth.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        last_name = request.form['last_name']
        patronymic = request.form['patronymic']
        group_number = request.form['group_number']

        # Валидация
        errors = []

        if not username or len(username) < 3:
            errors.append('Имя пользователя должно быть не менее 3 символов')

        if not email or '@' not in email:
            errors.append('Введите корректный email')

        if not last_name:
            errors.append('Укажите фамилию')

        if not patronymic:
            errors.append('Укажите отчество')

        if not group_number:
            errors.append('Укажите номер группы')

        if not password or len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')

        if password != confirm_password:
            errors.append('Пароли не совпадают')

        # Проверка существующего пользователя через ORM
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            errors.append('Пользователь с таким именем или email уже существует')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')

        # Создаём пользователя через ORM
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            last_name=last_name,
            patronymic=patronymic,
            group_number=group_number
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация успешна! Теперь войдите в систему, используя ваш email.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form

        # Поиск пользователя через ORM
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Обновляем дату последнего входа
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))
