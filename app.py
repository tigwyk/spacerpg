import os

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import flask_login
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import Result,User
from login import login_manager

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            flask_login.login_user(user)
            flash('You were logged in')
            next = flask.request.args.get('next')
            if not is_safe_url(next):
                return abort(400)
            return redirect(next or url_for('show_entries'))
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You were logged out')
    return redirect(url_for('show_entries'))
