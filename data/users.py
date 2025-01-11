import datetime
import sqlalchemy
from sqlalchemy.dialects.postgresql import ARRAY

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, 
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=datetime.datetime.now)
    favourites = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def add_to_favourites(self, product_id):
        if self.favourites is None:
            self.favourites = ''
        if str(product_id) not in self.favourites:
            self.favourites += str(product_id) + ';'

    def delete_from_favourites(self, product_id):
        if str(product_id) in self.favourites:
            self.favourites = self.favourites.replace(product_id + ";", "")
            

