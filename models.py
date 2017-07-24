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
    role = db.Column(db.String(64))

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
        self.role = 'user'

    def __repr__(self):
        return '<User #{} {}>'.format(self.id,self.email)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    type = db.Column(db.String(64))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Item {} {} #{}>'.format(self.name, self.type, self.id)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    npcs = db.relationship('NPC',backref='location',lazy='dynamic')
    players = db.relationship('Character', backref='location',lazy='dynamic')
    description = db.Column(db.String(256))
    exits = db.relationship('Room',lazy='joined')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Room {}#{}>'.format(self.name, self.id)

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    location_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    inventory = db.relationship('Item', backref='owner', secondary=npc_inventory_table)
    attributes = db.Column(JSON)
    credits = db.Column(db.Integer)
    hps = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name
        self.attributes = {'strength':5,'dexterity':5,'intelligence':5,'max_str':5, 'max_dex':5, 'max_int':5}
        self.credits = 0
        self.hps = self.attributes['strength']*3

    def __repr__(self):
        return '<NPC {}#{}>'.format(self.name, self.id)

player_inventory_table = db.Table('player_inventory_table', 
        db.Column('character_id', db.Integer, db.ForeignKey('character.id'), nullable=False),
        db.Column('item_id', db.Integer, db.ForeignKey('item.id'),nullable=False),
        db.Column('quantity', db.Integer),
        db.PrimaryKeyConstraint('character_id','item_id') )

npc_inventory_table = db.Table('npc_inventory_table',
        db.Column('npc_id', db.Integer, db.ForeignKey('npc.id'), nullable=False),
        db.Column('item_id', db.Integer, db.ForeignKey('item.id'),nullable=False),
        db.Column('quantity', db.Integer),
        db.PrimaryKeyConstraint('npc_id','item_id') )

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attributes = db.Column(JSON)
    inventory = db.relationship('Item', secondary=player_inventory_table, backref='owner')
    credits = db.Column(db.Integer)
    hps = db.Column(db.Integer)

    def __init__(self, name):
        str_max = random.uniform(9,11)
        dex_max = random.uniform(8,10)
        int_max = random.uniform(8,10)
        self.name = name
        self.attributes = {'strength':5, 'dexterity':5, 'intelligence':5,'max_str':str_max, 'max_dex':dex_max, 'max_int':int_max}
        self.credits = 0
        self.hps = self.attributes['strength']*3

    def __repr__(self):
        return '<Character {}#{}>'.format(self.name, self.id)



