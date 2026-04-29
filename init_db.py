# init_db.py
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, Item
import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Очищает существующие данные и создает новые таблицы."""
    init_database()
    click.echo('База данных успешно инициализирована.')

def init_database():
    """Инициализация БД и наполнение тестовыми данными."""
    db.create_all()

    # Создаём тестового админа, если его нет
    admin = User.query.filter_by(username='test_user').first()
    if not admin:
        admin = User(
            username='test_user',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            last_name='Тестов',
            patronymic='Тестович',
            group_number='123-A',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        click.echo('Создан тестовый пользователь: test_user / password123')

    # Создаём тестовые книги, если их нет
    if Item.query.count() == 0:
        # Получаем ID админа для связи
        admin_user = User.query.filter_by(username='test_user').first()
        admin_id = admin_user.id if admin_user else None

        test_books = [
            Item(
                title='Мастер и Маргарита',
                author='Михаил Булгаков',
                type='Книга',
                genre='Роман',
                status='Доступна',
                image_url='',
                description='Великий роман...'
            ),
            Item(
                title='Преступление и наказание',
                author='Фёдор Достоевский',
                type='Книга',
                genre='Роман',
                status='Доступна',
                image_url='',
                description='Психологический роман...'
            ),
            Item(
                title='1984',
                author='Джордж Оруэлл',
                type='Книга',
                genre='Антиутопия',
                status='На рассмотрении',
                image_url='',
                description='Роман-антиутопия...',
                suggested_by_user_id=admin_id
            ),
            Item(
                title='Автостопом по Галактике',
                author='Дуглас Адамс',
                type='Книга',
                genre='Фантастика',
                status='Доступна',
                image_url='',
                description='Культовая юмористическая фантастика.'
            ),
            Item(
                title='Убийство в Восточном экспрессе',
                author='Агата Кристи',
                type='Книга',
                genre='Детектив',
                status='Доступна',
                image_url='',
                description='Классический детектив с Эркюлем Пуаро.'
            ),
            Item(
                title='Гордость и предубеждение',
                author='Джейн Остин',
                type='Книга',
                genre='Классика',
                status='Доступна',
                image_url='',
                description='Знаменитый роман о любви и предрассудках.'
            ),
            Item(
                title='Homo Sapiens: Краткая история человечества',
                author='Юваль Ной Харари',
                type='Книга',
                genre='Научпоп',
                status='Доступна',
                image_url='',
                description='Масштабное исследование эволюции человека.'
            ),
            Item(
                title='Великий Гэтсби',
                author='Фрэнсис Скотт Фицджеральд',
                type='Книга',
                genre='Классика',
                status='Доступна',
                image_url='',
                description='История американской мечты.'
            ),
            Item(
                title='Цветы для Элджернона',
                author='Дэниел Киз',
                type='Книга',
                genre='Фантастика',
                status='Забронирована',
                image_url='',
                description='Трогательная научно-фантастическая история.'
            ),
            Item(
                title='Приключения Шерлока Холмса',
                author='Артур Конан Дойл',
                type='Книга',
                genre='Детектив',
                status='Доступна',
                image_url='',
                description='Сборник рассказов о знаменитом сыщике.'
            ),
            Item(
                title='Над пропастью во ржи',
                author='Джером Д. Сэлинджер',
                type='Книга',
                genre='Классика',
                status='На рассмотрении',
                image_url='',
                description='Культовый роман о подростковом бунте.'
            ),
            Item(
                title='Три товарища',
                author='Эрих Мария Ремарк',
                type='Книга',
                genre='Роман',
                status='Доступна',
                image_url='',
                description='Роман о дружбе, любви и жизни в послевоенной Германии.'
            ),
            Item(
                title='Понедельник начинается в субботу',
                author='Аркадий и Борис Стругацкие',
                type='Книга',
                genre='Фантастика',
                status='Доступна',
                image_url='',
                description='Сатирическая повесть о советских магах и ученых.'
            ),
            Item(
                title='Собачье сердце',
                author='Михаил Булгаков',
                type='Книга',
                genre='Сатира',
                status='Доступна',
                image_url='',
                description='Гениальная сатирическая повесть о превращении собаки в человека.'
            ),
            Item(
                title='Портрет Дориана Грея',
                author='Оскар Уайльд',
                type='Книга',
                genre='Философский роман',
                status='Доступна',
                image_url='',
                description='Роман о вечной молодости, красоте и разрушении души.'
            ),
            Item(
                title='Марсианин',
                author='Энди Вейер',
                type='Книга',
                genre='Научная фантастика',
                status='Доступна',
                image_url='',
                description='История астронавта, выживающего на Марсе в одиночестве.'
            ),
            Item(
                title='Дюна',
                author='Фрэнк Герберт',
                type='Книга',
                genre='Научная фантастика',
                status='Доступна',
                image_url='',
                description='Эпический роман о борьбе за власть на пустынной планете Арракис.'
            ),
            Item(
                title='О дивный новый мир',
                author='Олдос Хаксли',
                type='Книга',
                genre='Антиутопия',
                status='Доступна',
                image_url='',
                description='Классическая антиутопия о технологически развитом обществе будущего.'
            ),
            Item(
                title='Властелин колец',
                author='Дж. Р. Р. Толкин',
                type='Книга',
                genre='Фэнтези',
                status='Доступна',
                image_url='',
                description='Эпическая трилогия о борьбе добра и зла в Средиземье.'
            ),
        ]
        for book in test_books:
            db.session.add(book)
        db.session.commit()
        click.echo('База данных наполнена тестовыми книгами.')

