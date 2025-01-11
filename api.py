import json

from flask import Flask, Blueprint
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Blueprint('api', __name__, url_prefix='/api')
Base = declarative_base()


class Product(Base):
    # Определяем модель Product с полями id, name и price
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)


class Database:
    def __init__(self, db_path):
        # Создаем движок SQLAlchemy для подключения к базе данных
        self.engine = create_engine(f'sqlite:///{db_path}')
        # Создаем таблицы в базе данных, если они не существуют
        Base.metadata.create_all(self.engine)
        # Создаем фабрику сессий SQLAlchemy
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        # Метод для получения новой сессии SQLAlchemy
        return self.Session()


db = Database('db/products.db')  # Создаем экземпляр Database для работы с базой данных


@app.route('/id/<int:product_id>', methods=['GET'])
def get_product_info(product_id):
    # Обработчик GET-запроса для получения информации о продукте по его ID
    session = db.get_session()  # Получаем новую сессию SQLAlchemy
    product = session.query(Product).filter(Product.id == product_id).first()  # Находим продукт по ID
    session.close()  # Закрываем сессию
    if product:
        # Если продукт найден, возвращаем его информацию в формате JSON с поддержкой кириллицы
        return json.dumps({'id': product.id, 'name': product.name, 'price': product.price}, ensure_ascii=False)
    else:
        # Если продукт не найден, возвращаем ошибку 404
        return json.dumps({'error': 'Product not found'}), 404


@app.route('/list', methods=['GET'])
def get_product_list():
    # Обработчик GET-запроса для получения списка всех продуктов
    session = db.get_session()  # Получаем новую сессию SQLAlchemy
    products = session.query(Product).all()  # Получаем все продукты из базы данных
    session.close()  # Закрываем сессию
    product_list = [{'id': product.id, 'name': product.name, 'price': product.price} for product in products]
    # Создаем список словарей с информацией о продуктах
    return json.dumps(product_list,
                      ensure_ascii=False)  # Возвращаем список продуктов в формате JSON с поддержкой кириллицы


if __name__ == '__main__':
    app.run(debug=True)  # Запускаем Flask-приложение в режиме отладки
