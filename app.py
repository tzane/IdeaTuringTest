from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps
# import sqlite3

app = Flask(__name__)

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
    
@app.route('/')
@login_required    
def home():
    arguments = db.session.query(ArgumentPost).all()
    return render_template("index.html", arguments=arguments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = "Invalid credentials. Please try again."
        else:
            session['logged_in'] = True
            flash('You were just logged in!')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('about'))    

# def connect_db():
    # return sqlite3.connect(app.database)    
    
if __name__ == '__main__':
    app.run(debug=True)
