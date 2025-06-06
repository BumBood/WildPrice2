from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from random import shuffle

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    previous_price = Column(Float)
    image_url = Column(String)
    cat = Column(Integer)
    cat_name = Column(String)


class Database:
    def __init__(self, db_path):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def add(self, id, name, price, latest_price, image_url, cat, cat_name):
        new_product = Product(
            id=id,
            name=name,
            price=price,
            previous_price=latest_price,
            image_url=image_url,
            cat=cat,
            cat_name=cat_name,
        )
        self.session.add(new_product)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(e)
            return 1

    def update_price(self, id, new_price):
        try:
            product = self.session.query(Product).filter(Product.id == id).first()
            if product:
                product.price = new_price
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(e)
            return 1

    def update_previous_price(self, id, new_price):
        try:
            product = self.session.query(Product).filter(Product.id == id).first()
            if product:
                product.previous_price = new_price
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(e)
            return 1

    def get_price_from_id(self, id):
        product = self.session.query(Product).filter(Product.id == id).first()
        return product.price if product else None

    def get_name_from_id(self, id):
        product = self.session.query(Product).filter(Product.id == id).first()
        return product.name if product else None

    

    def get_price_from_name(self, name):
        products = self.session.query(Product).filter(Product.name == name).all()
        return [product.price for product in products] if products else None

    def get_all_product_ids(self):
        product_ids = [product.id for product in self.session.query(Product.id).all()]
        return product_ids

    def get_all_products(self):
        products = [product for product in self.session.query(Product).all()]
        shuffle(products)
        return products

    def get_all_products_sorted(self, sort_by="discount", reverse_sort=False):
        """
        Получить все товары с сортировкой по выбранному критерию.

        Args:
            sort_by (str): Критерий сортировки:
                - 'discount' (по умолчанию): сортировка по размеру скидки (от большей к меньшей)
                - 'name': сортировка по названию (по алфавиту)
                - 'price': сортировка по текущей цене (от меньшей к большей)
                - 'date': сортировка по ID (от новых к старым)
            reverse_sort (bool): Изменить порядок сортировки на обратный

        Returns:
            list: Отсортированный список товаров
        """
        products = [product for product in self.session.query(Product).all()]

        # Определяем базовое направление сортировки (до применения reverse_sort)
        base_reverse = False
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

        products.sort(key=key_func, reverse=final_reverse)
        return products

    def delete_product_by_id(self, id):
        try:
            # Находим продукт по ID
            product = self.session.query(Product).filter(Product.id == id).first()
            if product:
                # Удаляем найденный продукт
                self.session.delete(product)
                self.session.commit()
                return True
            return False  # Если продукт не найден, возвращаем False
        except Exception as e:
            self.session.rollback()
            print(e)
            return False

    def get_unique_categories_and_names(self):
        unique_categories = (
            self.session.query(Product.cat, Product.cat_name).distinct().all()
        )
        return unique_categories


if __name__ == "__main__":
    db = Database("products.db")
