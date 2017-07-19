from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from app import app,db,bcrypt


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))
    text = db.Column(db.String())

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<News #{}>'.format(self.id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(64), unique=True)
    _password = db.Column(db.Binary(60))
    character = db.relationship('Character',backref='user',uselist=False)

    @property

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
        return '<User #{} {}>'.format(self.id,self.email)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attributes = db.Column(JSON)
    inventory = db.relationship('Item', backref='container', lazy='dynamic')
    credits = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name
        self.attributes = {'Strength':0, 'Dexterity':0, 'Intelligence':0}
        self.inventory = []
        self.credits = 0

    def __repr__(self):
        return '<Character {}#{}>'.format(self.name, self.id)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    container_id = db.Column(db.Integer, db.ForeignKey('character.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Item {}#{}>'.format(self.name, self.id)

class Weapon(Item):
    def __repr__(self):
        return '<Weapon {}#{}>'.format(self.name, self.id)

class Armor(Item):
    def __repr__(self):
        return '<Armor {}#{}>'.format(self.name, self.id)
