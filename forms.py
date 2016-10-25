from flask_wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, StringField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional


class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(Form):
    username = TextField(
        'username',
        validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = TextField(
        'email',
        validators=[DataRequired(), Email(message=u'Invalid email address.'), Length(min=6, max=40)]
    )
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(), EqualTo('password', message='Passwords must match.')
        ]
    )
    
class ArgumentsForm(Form):
    # position = RadioField('Label', choices=[('value','description'),('value_two','whatever')])
    pro_abstract = StringField(
        'Pro abstract', 
        validators=[DataRequired(), Length(min=15, max=300)],
    )
    
    pro_argument = TextAreaField(
        'Pro argument',
        validators=[DataRequired(), Length(min=80, max=650)],
    )
    
    con_abstract = StringField(
        'Con abstract',
        validators=[DataRequired(), Length(min=15, max=300)],
    )
    
    con_argument = TextAreaField(
        'Con argument',
        validators=[DataRequired(), Length(min=80, max=650)],
    )

class VoteArgumentsForm(Form):
    first_vote = SelectField('first vote', choices=[(0,'-'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)], default=0, validators=[DataRequired(), NumberRange(min=1,max=10, message="Please pick a number!")], coerce=int)
    first_comment = StringField('first comment', validators=[Optional()])
    second_vote = SelectField('second vote', choices=[(0,'-'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)], default=0, validators=[DataRequired(), NumberRange(min=1,max=10, message="Please pick a number!")], coerce=int)
    # second_comment = StringField('second comment', validators=[Optional()])
    third_vote = SelectField('third vote', choices=[(0,'-'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)], default=0, validators=[DataRequired(), NumberRange(min=1,max=10, message="Please pick a number!")], coerce=int)
    # third_comment = StringField('third comment', validators=[Optional()])    