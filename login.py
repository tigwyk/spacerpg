import flask_login

from app import app

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    return User.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'