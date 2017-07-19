from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from app import app,db,bcrypt


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(JSON)
    result_no_stop_words = db.Column(JSON)

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(64), unique=True)
    _password = db.Column(db.Binary(60))

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User <{}> {}>'.format(self.id,self.email)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    
    attributes = db.Column(JSON)
    inventory = db.Column(JSON)

    def __init__(self, name):
        self.name = name
        self.attributes = {'Strength':0, 'Dexterity':0, 'Intelligence':0}
        self.inventory = []

    def __repr__(self):
        return 'Character <{}#{}>'.format(self.name, self.id)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Item <{}#{}>'.format(self.name, self.id)

class Weapon(Item):
    pass

class Armor(Item):
    pass
