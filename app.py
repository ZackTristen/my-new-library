# app.py
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db, login_manager
from models import User, Item, Reservation, ReadHistory
from auth import auth_bp
from datetime import datetime, timedelta
from init_db import init_db_command

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Конфигурация SQLAlchemy
# Указываем Flask, что база данных будет в папке 'instance'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Регистрация Blueprint
app.register_blueprint(auth_bp)

# Регистрация команды init-db
app.cli.add_command(init_db_command)


# Главная страница
@app.route('/')
@login_required
def index():
    search_query = request.args.get('search', '')
    genre = request.args.get('genre', '')
    status_filter = request.args.get('status', '')

    # Convert search_query to lowercase for case-insensitive Python-side comparison
    lower_search_query = search_query.lower()

    # Start with a base query
    base_query = Item.query

    if status_filter == 'Прочитано':
        # Книги, прочитанные пользователем
        query_items = ReadHistory.query.filter_by(user_id=current_user.id).join(Item)

        if genre:
            query_items = query_items.filter(Item.genre.ilike(f'%{genre}%'))

        read_history_entries = query_items.order_by(ReadHistory.read_at.desc()).all()
        # Extract Item objects for Python-side filtering
        initial_books = [entry.item for entry in read_history_entries]

    else:
        # Стандартная фильтрация
        if genre:
            base_query = base_query.filter(Item.genre.ilike(f'%{genre}%'))
        if status_filter:
            base_query = base_query.filter(Item.status == status_filter)

        initial_books = base_query.order_by(Item.created_at.desc()).all()


    # Apply search_query filtering in Python
    filtered_books = []
    if lower_search_query: # Only filter if there's a search query
        for book in initial_books:
            if lower_search_query in book.title.lower() or lower_search_query in book.author.lower():
                filtered_books.append(book)
    else:
        filtered_books = initial_books # If no search query, all initial books are valid

    books = filtered_books # Use the Python-filtered list


    # Получаем ID прочитанных книг
    read_history_entries = ReadHistory.query.filter_by(user_id=current_user.id).all()
    read_book_ids = {entry.item_id for entry in read_history_entries}

    # Конвертируем в словари для шаблона
    books_list = []
    for book in books:
        books_list.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'type': book.type,
            'genre': book.genre,
            'status': book.status,
            'image_url': book.image_url,
            'description': book.description,
            'created_at': book.created_at,
            'suggested_by_user_id': book.suggested_by_user_id
        })

    # Получаем список всех жанров для фильтра
    genres = db.session.query(Item.genre).filter(Item.genre.isnot(None)).distinct().order_by(Item.genre).all()
    genres = [g[0] for g in genres]

    return render_template(
        'index.html',
        books=books_list,
        current_user=current_user,
        search_query=search_query,
        current_genre=genre,
        current_status=status_filter,
        read_book_ids=read_book_ids,
        genres=genres
    )

# Детальная информация о книге
@app.route('/book/<int:item_id>')
@login_required
def book_details(item_id):
    book = Item.query.get(item_id)
    if book is None:
        abort(404)
    return render_template('book_details.html', book=book)


# --- Админ-панель ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Редактирование книги (только для админа)
@app.route('/book/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(item_id):
    book = Item.query.get_or_404(item_id)

    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.type = request.form['type']
        book.genre = request.form['genre']
        book.status = request.form['status']
        book.description = request.form['description']
        book.image_url = request.form['image_url']

        db.session.commit()
        flash('Информация о книге обновлена.', 'success')
        return redirect(url_for('book_details', item_id=item_id))

    return render_template('edit_book.html', book=book)


# Добавление книги
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        new_item = Item(
            title=request.form['title'],
            author=request.form['author'],
            type=request.form['type'],
            genre=request.form['genre'],
            status=request.form['status'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            suggested_by_user_id=current_user.id
        )

        db.session.add(new_item)
        db.session.commit()

        flash('Книга успешно предложена и отправлена на рассмотрение!', 'success')
        return redirect(url_for('index'))

    return render_template('add_book.html')


# API для бронирования
@app.route('/api/reserve', methods=['POST'])
@login_required
def reserve_book():
    data = request.get_json()
    book_id = data.get('book_id')

    book = Item.query.get(book_id)

    if book and book.status == 'Доступна':
        book.status = 'Забронирована'

        expires_at = datetime.utcnow() + timedelta(days=3)
        reservation = Reservation(
            item_id=book_id,
            user_id=current_user.id,
            expires_at=expires_at
        )

        db.session.add(reservation)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Книга забронирована!'})
    else:
        return jsonify({'success': False, 'message': 'Книга недоступна для бронирования'})


# Страница каталога пользователя
@app.route('/my_catalog')
@login_required
def my_catalog():
    user_id = current_user.id

    # Забронированные книги
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.reserved_at.desc()).all()

    # Предложенные книги
    suggested_books = Item.query.filter_by(suggested_by_user_id=user_id).order_by(Item.created_at.desc()).all()

    # Прочитанные книги
    read_history_entries = ReadHistory.query.filter_by(user_id=user_id).order_by(ReadHistory.read_at.desc()).all()

    return render_template(
        'my_catalog.html',
        reserved_books=reservations,
        suggested_books=suggested_books,
        read_books=read_history_entries
    )


# Отмена бронирования
@app.route('/reservations/delete/<int:reservation_id>', methods=['POST'])
@login_required
def delete_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)

    if reservation and reservation.user_id == current_user.id:
        item_id = reservation.item_id
        db.session.delete(reservation)

        # Обновляем статус книги
        item = Item.query.get(item_id)
        if item:
            item.status = 'Доступна'

        db.session.commit()
    else:
        flash('Бронирование не найдено или у вас нет прав на его отмену.', 'danger')

    return redirect(url_for('my_catalog'))


# Отметка книги как прочитанной
@app.route('/mark_read/<int:item_id>', methods=['POST'])
@login_required
def mark_as_read(item_id):
    existing = ReadHistory.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if not existing:
        read_entry = ReadHistory(user_id=current_user.id, item_id=item_id)
        db.session.add(read_entry)
        db.session.commit()
        flash('Книга отмечена как прочитанная!', 'success')
    else:
        flash('Эта книга уже в вашем списке прочитанных.', 'info')

    return redirect(url_for('index'))


# Снятие отметки о прочтении
@app.route('/unmark_read/<int:item_id>', methods=['POST'])
@login_required
def unmark_as_read(item_id):
    read_entry = ReadHistory.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    if read_entry:
        db.session.delete(read_entry)
        db.session.commit()
        flash('Отметка о прочтении снята.', 'success')

    return redirect(url_for('index'))


# --- Админ-панель ---

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    suggested_books = Item.query.filter_by(status='На рассмотрении').order_by(Item.created_at.desc()).all()
    return render_template('admin.html', suggested_books=suggested_books)


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    search_query = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    # Convert search_query to lowercase for case-insensitive Python-side comparison
    lower_search_query = search_query.lower()

    query = User.query
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    initial_users = query.order_by(User.created_at.desc()).all()

    # Apply search_query filtering in Python
    filtered_users = []
    if lower_search_query:
        for user in initial_users:
            if lower_search_query in user.username.lower() or \
               lower_search_query in user.email.lower() or \
               (user.last_name and lower_search_query in user.last_name.lower()):
                filtered_users.append(user)
    else:
        filtered_users = initial_users # If no search query, all initial users are valid

    users = filtered_users
    
    # Also need suggested_books for the 'books' tab in admin.html
    suggested_books = Item.query.filter_by(status='На рассмотрении').order_by(Item.created_at.desc()).all()
    
    return render_template(
        'admin.html',
        users=users,
        search_query=search_query,
        current_role=role_filter,
        suggested_books=suggested_books,
        active_tab='users'  # Indicate that the 'users' tab should be active
    )


@app.route('/admin/approve/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def approve_suggestion(item_id):
    item = Item.query.get(item_id)
    if item:
        item.status = 'Доступна'
        db.session.commit()
        flash('Книга одобрена и добавлена в общий каталог.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/reject/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def reject_suggestion(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Предложенная книга отклонена и удалена.', 'warning')
    return redirect(url_for('admin_panel'))


@app.route('/admin/users/toggle_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_role(user_id):
    user = User.query.get_or_404(user_id)
    
    # Нельзя снять права с самого себя
    if user.id == current_user.id:
        flash('Нельзя изменить свою собственную роль.', 'warning')
        return redirect(url_for('admin_users'))
    
    if user.role == 'admin':
        user.role = 'user'
        flash(f'Пользователь {user.username} теперь обычный пользователь.', 'info')
    else:
        user.role = 'admin'
        flash(f'Пользователь {user.username} теперь администратор.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete_selected', methods=['POST'])
@login_required
@admin_required
def delete_selected_users():
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        flash('Не выбрано ни одного пользователя.', 'warning')
        return redirect(url_for('admin_users'))
    
    deleted_count = 0
    for user_id in user_ids:
        user = User.query.get(int(user_id))
        if user and user.id != current_user.id:
            db.session.delete(user)
            deleted_count += 1
    
    db.session.commit()
    flash(f'Удалено пользователей: {deleted_count}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/delete_item/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Книга была успешно удалена из каталога.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
