from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin,current_user
from app import app,db,bcrypt
from flask import jsonify,redirect,url_for
from flask_admin.contrib.sqla import ModelView
import random

class CustomModelView(ModelView):
    create_modal = True
    edit_modal = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class AdminModelView(CustomModelView):
    column_editable_list = ['name']

class RoomModelView(CustomModelView):
    column_editable_list = ['name','description','type']

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
    description = db.Column(db.String(256))
    subtitle = db.Column(db.String(256))
    value = db.Column(db.Integer)
    slot = db.Column(db.String(32))

    def __init__(self, name='',type='',description='',subtitle='',value=0):
        self.name = name
        self.type = type
        self.description = description
        self.subtitle = subtitle
        self.value = value

    def __repr__(self):
        return '<Item {} {} #{}>'.format(self.name, self.type, self.id)

class Weapon(Item):
    id = db.Column(db.Integer, db.ForeignKey('item.id'),primary_key=True)
    damage_dice = db.Column(db.String(32))

    @property
    def is_weapon():
        return True

    def __init__(self, name='',damage_dice=''):
        self.name = name
        self.damage_dice = damage_dice
        self.slot = 'weapon'

    def __repr__(self):
        return '<Weapon {}#{}>'.format(self.name, self.id)

class Armor(Item):
    id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    ac = db.Column(db.Integer)

    @property
    def is_armor():
        return True

    def __init__(self, name='',ac=0,slot='chest',value=0):
        self.name = name
        self.ac = ac
        self.slot = slot
        self.value = value

    def __repr__(self):
        return '<Armor {}#{}>'.format(self.name, self.id)

room_exits_table = db.Table('room_exits_table',
        db.Column('room1_id',db.Integer,db.ForeignKey('room.id'),primary_key=True),
        db.Column('room2_id',db.Integer,db.ForeignKey('room.id'),primary_key=True)
        )

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    players = db.relationship('Character', backref='location',lazy='dynamic')
    description = db.Column(db.String(256))
    exit_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    exits = db.relationship('Room', secondary=room_exits_table,
            primaryjoin=id==room_exits_table.c.room1_id,
            secondaryjoin=id==room_exits_table.c.room2_id,
            backref='linked_rooms'
            )
    type = db.Column(db.String(64))

    def __init__(self, name='',description='',type='',players=[],exits=[]):
        self.name = name
        self.description = description
        self.type = type
        self.players = players
        self.exits = exits

    def __repr__(self):
        return '<Room {}#{}>'.format(self.name, self.id)

inventory_table = db.Table('inventory_table', 
        db.Column('living_id', db.Integer, db.ForeignKey('living.id'),nullable=False),
        db.Column('item_id', db.Integer, db.ForeignKey('item.id'),nullable=False),
        db.PrimaryKeyConstraint('living_id', 'item_id') )

class Living(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    inventory = db.relationship('Item', secondary=inventory_table)
    attributes = db.Column(MutableDict.as_mutable(JSON))
    body = db.Column(MutableDict.as_mutable(JSON))
    credits = db.Column(db.Integer)
    race = db.Column(db.String(64))
    hps = db.Column(db.Integer)
    max_hps = db.Column(db.Integer)

    def __init__(self, name='',race='human'):
        str_max = random.uniform(9,11)
        dex_max = random.uniform(8,10)
        int_max = random.uniform(8,10)
        self.name = name
        self.attributes = {'strength':5, 'dexterity':5, 'intelligence':5,'max_str':str_max, 'max_dex':dex_max, 'max_int':int_max}
        self.credits = 0
        self.race = race
        self.max_hps = self.attributes['strength']*3
        self.hps = self.max_hps
        self.body = {'head':None,'chest':None, 'hands':None,'legs':None,'feet':None,'weapon':None}


    def dexterity_roll(self):
        dex = self.attributes['dexterity']
        roll = random.uniform(0, dex)
        return roll

    def attack(self, opponent):
        if combat_hit_check(self, opponent):
            wielded_weapon_id = self.body['weapon']
            if not wielded_weapon_id:
                damage = random.randint(0,int(self.attributes['strength']))
                opponent.take_damage(damage)
                return damage
            else:
                wielded_weapon = Weapon.query.get(wielded_weapon_id)
                num_dice,sides = wielded_weapon.damage_dice.split('d')
                num_dice = int(num_dice)
                sides = int(sides)
                total_roll = 0

                for i in range(1,num_dice):
                    roll_result = random.randint(1,sides)
                    total_roll += roll_result

                damage = total_roll
                #target_body_part = roll_for_body_part()
                #if armor_absorb fails
                damage_done = opponent.take_damage(damage)
                return damage_done
        else:
            return -1
                
    def take_damage(self, damage):
        #armor absorbtion
        damage_taken = damage
        self.hps = self.hps - damage_taken
        db.session.add(self)
        db.session.commit()
        return damage_taken

    def equip(self, item):
        if not item:
            return False

        self.body[item.slot] = item.id
        db.session.add(self)
        db.session.commit()
        return True

class NPC(Living):
    __tablename__ = 'npc'
    id = db.Column(db.Integer, db.ForeignKey('living.id'),primary_key=True)

    def __repr__(self):
        return '<NPC {}#{}>'.format(self.name, self.id)

    def die(self, killer):
        msg = '{} killed {}.'.format(killer.name, self.name)
        db.session.delete(self)
        db.session.commit()
        return msg


class Character(Living):
    id = db.Column(db.Integer, db.ForeignKey('living.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    title = db.Column(db.String(128))
    opponent_id = db.Column(db.Integer, db.ForeignKey('npc.id'))
    opponent = db.relationship('NPC',backref='opponent',foreign_keys=[opponent_id])

    def __repr__(self):
        return '<Character {}#{}>'.format(self.name, self.id)

def roll_for_body_part():
    body_parts = ['head','chest','hands','legs','feet']
    bias_list = [0.10,0.50,0.05,0.30,0.05]

    roll = random.uniform(0, sum(bias_list))
    current = 0
    for i, bias in enumerate(bias_list):
        current += bias
        if roll <= current:
            return i+1

def combat_hit_check(player, npc):
    if player.dexterity_roll() > npc.dexterity_roll():
        return True
    else:
        return False
