from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from functools import wraps
from forms import LoginForm, RegisterForm
import random
# import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

import os

app.secret_key = "my precious"
# app.database = "sample.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arguments.db'

# create the sqlalchemy object
db = SQLAlchemy(app)

from models import *

@app.route('/about')
def about():
    """
    Needs to return about.html
    """
    return "This is the about page!"
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(request.form['name'], request.form['email'],
                    request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html')    

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/arguments', methods=['GET','POST'])    
@login_required       
def add_arguments():
    user_position = False
    if request.method == 'POST':
        if request.form['user_stance'] == "pro":
            user_position = True
        pro_argument = ArgumentPost("$15 Federal Minimum Wage", True, user_position, request.form['abstract'], request.form['argument'], session['user_id'])
        con_argument = ArgumentPost("$15 Federal Minimum Wage", False, user_position, request.form['abstract1'], request.form['argument1'], session['user_id'])
        db.session.add(pro_argument)
        db.session.add(con_argument)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('arguments.html')
    

@app.route('/', methods=['GET','POST'])
@login_required    
def home():
    if request.method == 'POST':
        argument_ids = session['argument_ids']
        votes = request.form.getlist('vote_value')
        for position, vote in enumerate(votes):
            vote_record = Vote(argument_ids[position], int(vote), int(session['user_id']))
            db.session.add(vote_record)
        db.session.commit()
    user_argument = db.session.query(ArgumentPost).filter_by(topic="The federal government should impose a national $15/hr minimum wage.",id=session['user_id']).first()
    if user_argument.user_procon == True:
        user_status = True
        displayable_arguments = db.session.query(ArgumentPost).filter_by(procon_topic=True).all()
    else:
        user_status = False
        displayable_arguments = db.session.query(ArgumentPost).filter_by(procon_topic=False).all()
    userless_arguments = [argument for argument in displayable_arguments if argument.author_id != session['user_id']]  
    arguments = random.sample(userless_arguments, 3)
    session['argument_ids'] = [argument.id for argument in arguments]
    return render_template("index.html", user_status=user_status, arguments=arguments)

@app.route('/login', methods=['GET', 'POST'])    
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['username']).first()
        if user is not None and bcrypt.check_password_hash(
            user.password, request.form['password']
        ):
            session['logged_in'] = True
            session['user_id'] = user.id
            flash('You were logged in.')
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password.'            
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('about'))    

# def connect_db():
    # return sqlite3.connect(app.database)    
    
if __name__ == '__main__':
    app.run(debug=True)
