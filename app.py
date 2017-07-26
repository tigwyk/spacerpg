import os

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import flask_login
from urllib.parse import urlparse, urljoin
from flask_sqlalchemy import SQLAlchemy
from flask_vue import Vue
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['VUE_USE_MINIFIED'] = True

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

Vue(app)

from models import News,User,Character,Item,NPC,Room
from login import login_manager
from forms import RegistrationForm,LoginForm,CharacterCreationForm


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc

@app.route('/')
@flask_login.login_required
def index():
    news = News.query.all()
    return render_template('index.html', news=news,character=flask_login.current_user.character)

@app.route('/add', methods=['POST'])
@flask_login.login_required
def add_entry():
    flash('New entry was successfully posted')
    return redirect(url_for('index'))

@app.route('/register', methods=['POST','GET'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash('Email address already exists','error')
                return redirect(url_for('register'))
            else:
                user = User(
                        email = form.email.data,
                        password = form.password.data
                        )
                db.session.add(user)
                db.session.commit()
                flash('Registered succesfully!','error')
                flask_login.login_user(user)
                return redirect(url_for('index'))
        else:
            flash('Form failed to validate','error')
            return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('Email address not found','error')
                return redirect(url_for('login'))
            if bcrypt.check_password_hash(user.password, form.password.data):
                flask_login.login_user(user,remember=True)
                flash('You were logged in','error')
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for('index'))
            else:
                flash('Incorrect password','error')
                return redirect(url_for('login'))
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You were logged out','error')
    return redirect(url_for('index'))

@app.route('/character', methods=['GET', 'POST'])
@flask_login.login_required
def character_profile():
    form = CharacterCreationForm()
    if request.method == 'GET':
        char = flask_login.current_user.character
        if char is None:
            return render_template('character_profile.html',form=form)    
        else:
            return render_template('character_profile.html',character=char)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if Character.query.filter_by(name=form.name.data).first():
                flash('Character name already in use. Try again.','error')
                return redirect(url_for('character_profile'))
            else:
                character = Character(form.name.data)
                db.session.add(character)
                flask_login.current_user.character = character
                db.session.add(flask_login.current_user)
                db.session.commit()
                character.move_to(Room.query.first())
                flash('Character created! Welcome to Phobos!','error')
                return redirect(url_for('character_profile'))
        else:
            flash('Failed to validate form','error')
            return redirect(url_for('character_profile'))


@app.route('/inventory')
@flask_login.login_required
def inventory():
    char = flask_login.current_user.character
    if char is None:
        return redirect(url_for('character_profile'))    
    else:
        inventory
        return render_template('inventory.html',inventory=inv)

@app.route('/move/<destination_id>')
@flask_login.login_required
def move_character():
    char = flask_login.current_user.character
    if char is None:
        return redirect(url_for('character_profile'))

    destination = Room.query.get_or_404(destination_id)
    if destination != char.location and destination in char.location.exits:
        char.location = destination
    
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
        return redirect(url_for('login'))

#Game Logic Stuff

