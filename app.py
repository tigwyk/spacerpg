import os

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import flask_login
from urllib.parse import urlparse, urljoin
from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from models import News,User
from login import login_manager
from forms import RegistrationForm,LoginForm,CharacterCreationForm


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc

@app.route('/')
def show_entries():
    entries = ""
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
@flask_login.login_required
def add_entry():
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['POST','GET'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash('Email address already exists')
                return redirect(url_for('register'))
            else:
                user = User(
                        email = form.email.data,
                        password = form.password.data
                        )
                db.session.add(user)
                db.session.commit()
                flash('Registered succesfully!')
                flask_login.login_user(user)
                return redirect(url_for('show_entries'))
        else:
            flash('Form failed to validate')
            return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('Email address not found')
                return redirect(url_for('login'))
            if bcrypt.check_password_hash(user.password, form.password.data):
                flask_login.login_user(user,remember=True)
                flash('You were logged in')
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for('show_entries'))
            else:
                flash('Incorrect password')
                return redirect(url_for('login'))
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You were logged out')
    return redirect(url_for('show_entries'))

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
                flash('Character name already in use. Try again.')
                return redirect(url_for('character_profile'))
            else:
                character = Character(form.name.data)
                db.session.add(character)
                db.session.commit()
                flash('Character created! Welcome to Phobos!')
                return redirect(url_for('character_profile'))
