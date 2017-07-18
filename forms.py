from flask_wtf import Form
from wtforms import BooleanField, StringField, PasswordField, validators

class RegistrationForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
                    ])  
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6)])
    password = PasswordField('Password')

