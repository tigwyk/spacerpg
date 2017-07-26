from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin,current_user
from app import app,db,bcrypt
from flask import jsonify,redirect,url_for
from flask_admin.contrib.sqla import ModelView
import random

class AdminModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

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

    def __init__(self, email='', password=''):
        self.email = email
        self.password = password
        self.role = 'user'

    def __repr__(self):
        return '<User #{} {}>'.format(self.id,self.email)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    type = db.Column(db.String(64))

    def __init__(self, name='',type='',damage=0):
        self.name = name

    def __repr__(self):
        return '<Item {} {} #{}>'.format(self.name, self.type, self.id)

class Weapon(Item):
    id = db.Column(db.Integer, db.ForeignKey('item.id'),primary_key=True)
    damage = db.Column(db.Integer)

    def __init__(self, name='',damage=0):
        self.name = name
        self.damage = damage

    def __repr__(self):
        return '<Weapon {}#{}>'.format(self.name, self.id)

class Armor(Item):
    id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    ac = db.Column(db.Integer)
    
    def __init__(self, name='',ac=0):
        self.name = name
        self.ac = ac

    def __repr__(self):
        return '<Armor {}#{}>'.format(self.name, self.id)



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    players = db.relationship('Character', backref='location',lazy='dynamic')
    description = db.Column(db.String(256))
    exit_id = db.Column(db.Integer, db.ForeignKey('room.id'), index=True)
    exits = db.relationship('Room', remote_side=[id],backref='linked_rooms',uselist=True)
    type = db.Column(db.String(64))

    def __init__(self, name='',description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Room {}#{}>'.format(self.name, self.id)

inventory_table = db.Table('inventory_table', 
        db.Column('character_id', db.Integer, db.ForeignKey('character.id')),
        db.Column('npc_id', db.Integer, db.ForeignKey('npc.id')), 
        db.Column('item_id', db.Integer, db.ForeignKey('item.id'),nullable=False),
        db.PrimaryKeyConstraint('character_id','npc_id', 'item_id') )

class NPC(db.Model):
    __tablename__ = 'npc'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    inventory = db.relationship('Item', secondary=inventory_table)
    attributes = db.Column(JSON)
    credits = db.Column(db.Integer)
    opponent_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    hps = db.Column(db.Integer)

    def __init__(self, name='',credits=0):
        self.name = name
        self.attributes = {'strength':5,'dexterity':5,'intelligence':5,'max_str':5, 'max_dex':5, 'max_int':5}
        self.credits = 0
        self.hps = self.attributes['strength']*3

    def __repr__(self):
        return '<NPC {}#{}>'.format(self.name, self.id)

    def dexterity_roll(self):
        dex = self.attributes['dexterity']
        roll = random.uniform(0, dex)
        return roll

    def take_damage(self, attacker, damage):
        if damage >= self.hps:
            self.die(attacker)
        else:
            self.hps = self.hps - damage

    def die(self, killer):
        msg = '{} killed {}.'.format(killer.name, self.name)
        db.session.delete(self)
        db.session.commit()
        return jsonify(msg)


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attributes = db.Column(JSON)
    inventory = db.relationship('Item', secondary=inventory_table)
    credits = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    opponent = db.relationship('NPC',uselist=False,backref='opponent')
    hps = db.Column(db.Integer)

    def __init__(self, name=''):
        str_max = random.uniform(9,11)
        dex_max = random.uniform(8,10)
        int_max = random.uniform(8,10)
        self.name = name
        self.attributes = {'strength':5, 'dexterity':5, 'intelligence':5,'max_str':str_max, 'max_dex':dex_max, 'max_int':int_max}
        self.credits = 0
        self.hps = self.attributes['strength']*3

    def __repr__(self):
        return '<Character {}#{}>'.format(self.name, self.id)

    def dexterity_roll(self):
        dex = self.attributes['dexterity']
        roll = random.uniform(0, dex)
        return roll

    def attack(self, npc):
        if combat_hit_check(self, npc):
            damage = 1
            #if armor_absorb fails
            npc.take_damage(self, damage)
            return jsonify('You hit {} for {} damage.'.format(npc.name, damage))
        else:
            return jsonify('You missed {}.'.format(npc.name))

def combat_hit_check(player, npc):
    if player.dexterity_roll() > npc.dexterity_roll():
        return True
    else:
        return False
