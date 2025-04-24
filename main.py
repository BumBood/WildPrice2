import os
import sys
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user
from flask_login import login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from api import app as api_app

from data import db_session
from data.users import User
from db.products_db import Database
from forms.user import RegisterForm
from parser.wildberries_parser import get_info, get_image_url, get_url, get_sale
from parser.model import Item
import requests
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Добавляем путь к папке parser в sys.path
sys.path.append(os.path.join(BASE_DIR, "parser"))


class LoginForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


app = Flask(__name__)
app.register_blueprint(api_app)

app.config["SECRET_KEY"] = "omegaultra_secret_key"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():  # Renamed from login()
    sort_by = request.args.get(
        "sort_by", "discount"
    )  # По умолчанию сортировка по размеру скидки
    reverse_sort = (
        request.args.get("reverse", "0") == "1"
    )  # Обратная сортировка (0 - нет, 1 - да)

    return render_template(
        "main_content.html",
        title="Wildprice",
        Database=Database,
        sort_by=sort_by,
        reverse_sort=reverse_sort,
    )


@app.route("/favourites")
def favourites():  # Страница с избранными
    sort_by = request.args.get(
        "sort_by", "discount"
    )  # По умолчанию сортировка по размеру скидки
    reverse_sort = (
        request.args.get("reverse", "0") == "1"
    )  # Обратная сортировка (0 - нет, 1 - да)

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        if user.favourites:
            favourites = list(
                map(lambda x: int(x), user.favourites.strip().split(";")[:-1])
            )  # получаем список избранных товаров
        else:
            favourites = []

        products_db = Database("db/products.db")

        # Получаем информацию о всех избранных товарах из локальной базы данных
        products_info = {}
        sorted_favourites = favourites.copy()  # Сначала просто копируем список

        # Получаем все товары из БД
        all_products = products_db.get_all_products()

        # Фильтруем только избранные товары
        favorite_products = [
            product for product in all_products if product.id in favourites
        ]

        # Определяем базовое направление сортировки
        base_reverse = False

        # Применяем сортировку к списку товаров
        if sort_by == "discount":
            # По умолчанию - от большей скидки к меньшей
            base_reverse = True
            key_func = lambda p: (
                (p.previous_price - p.price) / p.previous_price
                if p.previous_price > 0
                else 0
            )
        elif sort_by == "name":
            # По умолчанию - по алфавиту A-Z
            key_func = lambda p: p.name.lower()
        elif sort_by == "price":
            # По умолчанию - от меньшей к большей
            key_func = lambda p: p.price
        elif sort_by == "date":
            # По умолчанию - от новых к старым
            base_reverse = True
            key_func = lambda p: p.id

        # Если запрошена обратная сортировка, инвертируем базовое направление
        final_reverse = base_reverse
        if reverse_sort:
            final_reverse = not base_reverse

        # Сортируем список товаров
        favorite_products.sort(key=key_func, reverse=final_reverse)

        # Создаем отсортированный список ID и словарь с информацией о товарах
        sorted_favourites = [product.id for product in favorite_products]
        for product in favorite_products:
            products_info[product.id] = product

        return render_template(
            "favourites_content.html",
            title="Wildprice",
            products_info=products_info,
            favourites=favourites,
            sorted_favourites=sorted_favourites,
            get_categories=products_db.get_unique_categories_and_names,
            sort_by=sort_by,
            reverse_sort=reverse_sort,
        )
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/register", methods=["GET", "POST"])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/category/<int:category_id>")
def show_category(category_id):
    sort_by = request.args.get(
        "sort_by", "discount"
    )  # По умолчанию сортировка по размеру скидки
    reverse_sort = (
        request.args.get("reverse", "0") == "1"
    )  # Обратная сортировка (0 - нет, 1 - да)

    products_db = Database("db/products.db")

    # Получаем все товары с указанной категорией
    all_products = products_db.get_all_products_sorted(sort_by, reverse_sort)

    # Фильтруем товары категории
    category_products = [p for p in all_products if int(p.cat[4:]) == category_id]
    has_products = len(category_products) > 0

    # Получаем название категории из товаров категории, а не из всех товаров
    category_name = None
    if has_products:
        category_name = category_products[0].cat_name
    else:
        # Если товаров в категории нет, получаем название напрямую
        unique_categories = products_db.get_unique_categories_and_names()
        for cat, cat_name in unique_categories:
            if int(cat[4:]) == category_id:
                category_name = cat_name
                break

    # Если не удалось получить имя категории, используем "Категория" как запасной вариант
    if not category_name:
        category_name = "Категория"

    return render_template(
        "category.html",
        title=f"{category_name} - Wildprice",
        Database=Database,
        category_id=category_id,
        category_name=category_name,
        sort_by=sort_by,
        reverse_sort=reverse_sort,
        has_products=has_products,
        category_products=category_products,  # Передаем отфильтрованные товары категории
    )


@app.route("/add_to_favourites/<int:product_id>", methods=["GET"])
def add_to_favourites(product_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        user = db_sess.query(User).get(current_user.id)
        user.add_to_favourites(product_id)

        db_sess.commit()

        # Проверяем если это AJAX запрос
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})

    # Если пользователь не авторизован или не AJAX запрос, редирект
    if not current_user.is_authenticated:
        return redirect(url_for("register"))
    return redirect(url_for("index"))


@app.route("/delete_from_favourites/<int:product_id>", methods=["GET"])
def delete_from_favourites(product_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        user = db_sess.query(User).get(current_user.id)
        user.delete_from_favourites(str(product_id))

        db_sess.commit()

        # Проверяем если это AJAX запрос
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})

    # Если пользователь не авторизован или не AJAX запрос, редирект
    if not current_user.is_authenticated:
        return redirect(url_for("register"))
    return redirect(url_for("favourites"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/category/cat=<int:category_id>")
def wrong_category_url_2(category_id):
    """Обрабатывает ошибочный URL вида /category/cat=ID"""
    # Сохраняем параметры сортировки
    sort_by = request.args.get("sort_by", "discount")
    reverse_sort = request.args.get("reverse", "0")

    # Перенаправляем на правильный URL
    return redirect(
        url_for(
            "show_category",
            category_id=category_id,
            sort_by=sort_by,
            reverse=reverse_sort,
        )
    )


@app.route("/category/<path:path>")
def catch_all_category(path):
    """Обрабатывает любые неверные форматы URL для категорий"""
    # Пытаемся извлечь ID категории из пути
    match = re.search(r"(\d+)", path)
    if match:
        category_id = int(match.group(1))
        # Сохраняем параметры сортировки
        sort_by = request.args.get("sort_by", "discount")
        reverse_sort = request.args.get("reverse", "0")

        # Перенаправляем на правильный URL
        return redirect(
            url_for(
                "show_category",
                category_id=category_id,
                sort_by=sort_by,
                reverse=reverse_sort,
            )
        )

    # Если не удалось извлечь ID категории, перенаправляем на главную
    return redirect(url_for("index"))


if __name__ == "__main__":
    db_session.global_init("db/users.db")
    app.run(host="0.0.0.0", debug=True)
