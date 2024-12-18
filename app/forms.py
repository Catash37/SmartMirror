# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    face_image = FileField('Upload Face Image', validators=[DataRequired()])
    time_zone = SelectField('Time Zone', choices=[
        ('UTC', 'UTC'),
        ('America/New_York', 'New York'),
        ('Europe/London', 'London'),
        ('Asia/Tokyo', 'Tokyo'),
        ('Australia/Sydney', 'Sydney'),
    ], validators=[DataRequired()])
    submit = SubmitField('Register')
