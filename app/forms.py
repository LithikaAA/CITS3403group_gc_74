from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DateField, SubmitField
from wtforms.validators import Optional, Length, Email
from flask_wtf.file import FileField, FileAllowed

class AccountForm(FlaskForm):
    name    = StringField(
        'Full Name',
        validators=[Optional(), Length(max=100)]
    )
    gender  = RadioField(
        'Gender',
        choices=[('Male','Male'),('Female','Female'),('Other','Other')],
        validators=[Optional()]
    )
    dob     = DateField(
        'Date of Birth',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    email   = StringField(
        'Email Address',
        validators=[Optional(), Email(), Length(max=120)]
    )
    mobile  = StringField(
        'Mobile Number',
        validators=[Optional(), Length(max=20)]
    )
    picture = FileField(
        'Profile Picture',
        validators=[FileAllowed(['jpg','png','jpeg'], 'Only images allowed')]
    )
    submit  = SubmitField('Save Changes')
