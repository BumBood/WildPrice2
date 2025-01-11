import os
import sys

from flask import Flask, render_template, redirect, url_for, flash
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
from parser.wildberries_parser import get_info

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Добавляем путь к папке parser в sys.path
sys.path.append(os.path.join(BASE_DIR, 'parser'))

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


app = Flask(__name__)
app.register_blueprint(api_app)

app.config['SECRET_KEY'] = 'omegaultra_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():  # Renamed from login()
    return render_template('main_content.html', title='Wildprice', Database=Database)

@app.route('/favourites')
def favourites():  # Страница с избранными
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)

        favourites = list(map(lambda x: int(x), user.favourites.strip().split(";")[:-1])) # получаем список избранных товаров
        if len(favourites) == 0:
            flash('У вас нет избранных! ')

        print(favourites)

        return render_template('favourites_content.html', title='Wildprice', get_info=get_info, favourites=favourites)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/add_to_favourites/<int:product_id>', methods=['GET'])
def add_to_favourites(product_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        user = db_sess.query(User).get(current_user.id)
        user.add_to_favourites(product_id)

        db_sess.commit()
    return redirect(url_for('index'))

@app.route('/delete_from_favourites/<int:product_id>', methods=['GET'])
def delete_from_favourites(product_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        user = db_sess.query(User).get(current_user.id)
        user.delete_from_favourites(str(product_id))

        db_sess.commit()

    return redirect(url_for('favourites'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")




if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(debug=True)
