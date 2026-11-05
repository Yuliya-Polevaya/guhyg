from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pymysql
db = pymysql.connect(
    host="localhost",
    user="root",
    password="1111",
    database="django",
    charset="utf8mb4"
)
print(db)

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1111@localhost/django'
# db = SQLAlchemy(app)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'


@app.route('/about')
def about():
    return '💗💗💗✝'


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/prod')
def prod():
    with db.cursor() as cursor:
        sql = "SELECT p.id, p.name, p.sale, p.material, p.date_prod, p.counter, c.title AS category_name FROM myproj_product p JOIN myproj_categorii c ON p.cat_id_id = c.id"
        cursor.execute(sql)
        users = cursor.fetchall()
        print(users)

        for user in users:
            print(f"ID: {user[0]}, name: {user[1]}, sale: {user[2]}, material: {user[3]}, date_prod: {user[4]}, counter: {user[5]}, cat_id_id: {user[6]}")

    with db.cursor() as cursor:
        sql = "SELECT * FROM django.myproj_categorii"
        cursor.execute(sql)
        us = cursor.fetchall()
        print(us)

        for u in us:
            print(f"ID: {u[0]}, title: {u[1]}, comment: {u[2]}")

        return render_template('prod.html', name=users, name2=us)


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/onas')
def onas():
    return render_template('onas.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form.get('name', '')
        age  = request.form.get('age', '')
        print(name, age)
        return f"Это профиль пользователя {name}, возраст {age}"

    return '''
        <form method="post">
            <input type="text"   name="name" placeholder="Имя"><br>
            <input type="number" name="age"  placeholder="Возраст"><br>
            <button type="submit">Отправить</button>
        </form>
    '''


@app.route('/admin', methods=['GET', 'POST'])
def dosup():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        # 1. Валидация
        if not login or not password:
            return render_template('login.html', error="Введите логин и пароль!")

        # 2. Запрос в БД (наша новая таблица myproj_admin)
        with db.cursor() as cursor:
            sql = "SELECT id, login FROM myproj_admin WHERE login=%s AND password=%s"
            cursor.execute(sql, (login, password))
            user = cursor.fetchone()

        # 3. Проверка результата
        if user:
            # Если совпадает — записываем в сессию
            session['admin_logged_in'] = True
            session['admin_name'] = user[1]
            return redirect(url_for('admin_panel'))
        else:
            # Если не совпадает — показываем форму с ошибкой
            return render_template('login.html', error="Неверный логин или пароль")

    # Если это GET-запрос, показываем форму входа из шаблона
    return render_template('login.html')


@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('dosup'))
    return render_template('admin.html')


# --- РАЗДЕЛ КАТЕГОРИЙ ---
@app.route('/admin_panel/categories', methods=['GET', 'POST'])
def admin_categories():
    if not session.get('admin_logged_in'): return redirect(url_for('dosup'))

    if request.method == 'POST':
        title = request.form.get('title')
        comment = request.form.get('comment')
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO myproj_categorii (title, comment) VALUES (%s, %s)", (title, comment))
        db.commit()
        return redirect(url_for('admin_categories'))

    with db.cursor() as cursor:
        cursor.execute("SELECT id, title, comment FROM myproj_categorii")
        items = cursor.fetchall()
    return render_template('admin_categories.html', items=items)


# --- РАЗДЕЛ ТОВАРОВ ---
@app.route('/admin_panel/products', methods=['GET', 'POST'])
def admin_products():
    if not session.get('admin_logged_in'): return redirect(url_for('dosup'))

    if request.method == 'POST':
        p_name = request.form.get('p_name')
        p_sale = request.form.get('p_sale')
        p_cat_id = request.form.get('p_cat_id')
        p_material = request.form.get('material', 'Не указано') # <-- Получаем материал из формы
        
        with db.cursor() as cursor:
            # ДОБАВЛЕНО: material в список полей и %s в значения
            sql = "INSERT INTO myproj_product (name, sale, cat_id_id, material, date_prod, counter) VALUES (%s, %s, %s, %s, NOW(), 1)"
            cursor.execute(sql, (p_name, p_sale, p_cat_id, p_material)) # <-- Добавили p_material в кортеж
        db.commit()
        return redirect(url_for('admin_products'))

    with db.cursor() as cursor:
        cursor.execute("SELECT id, name, sale FROM myproj_product")
        items = cursor.fetchall()
        cursor.execute("SELECT id, title FROM myproj_categorii")
        categories = cursor.fetchall()
    return render_template('admin_products.html', items=items, categories=categories)


# --- РАЗДЕЛ ПОЛЬЗОВАТЕЛЕЙ ---
@app.route('/admin_panel/users', methods=['GET', 'POST'])
def admin_users():
    if not session.get('admin_logged_in'): return redirect(url_for('dosup'))

    if request.method == 'POST':
        u_name = request.form.get('u_name')
        u_age = request.form.get('u_age')
        with db.cursor() as cursor:
            # В вашей таблице myproj_userprofile колонки: id, name, age
            cursor.execute("INSERT INTO myproj_userprofile (name, age) VALUES (%s, %s)", (u_name, u_age))
        db.commit()
        return redirect(url_for('admin_users'))

    with db.cursor() as cursor:
        cursor.execute("SELECT id, name, age FROM myproj_userprofile")
        items = cursor.fetchall()
    return render_template('admin_users.html', items=items)


@app.route('/logout')
def logout():
    session.clear()  # Выходим
    return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True)