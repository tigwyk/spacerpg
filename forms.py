from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
                    ])  
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6)])
    password = PasswordField('Password')

class CharacterCreationForm(FlaskForm):
    name = StringField('Character Name', [validators.Length(min=3, max=35)])

class ItemCreationForm(FlaskForm):
    name = StringField('Item Name', [validators.Length(min=1)])
