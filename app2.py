from flask import Flask, render_template, redirect, url_for, request, session, flash, g, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from functools import wraps
from forms import LoginForm, RegisterForm
from sqlalchemy.sql import func
import random
# import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

import os

app.secret_key = "my precious"
# app.database = "sample.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arguments2.db'

# create the sqlalchemy object
db = SQLAlchemy(app)

from models2 import *

@app.route('/')
def home():
    all_topics = db.session.query(Topic).all()
    other_categories = db.session.query(Topic.category).distinct()
    user_available_motions = [{} for x in xrange(len(list(other_categories)))]
    for index, cat in enumerate(other_categories):
        temp_list = []
        for top in all_topics:
            if str(cat[0]) == str(top.category):
                temp_list.append(top)
            else:
                pass
        user_available_motions[index][str(cat[0])] = temp_list   
    all_motions = [i for i in user_available_motions if i.values()[0] != []]
    user_status = None
    try:
        if session['logged_in'] == True:
            user_status = True
    except KeyError:
        return render_template('about.html', user_status = user_status, all_motions = all_motions)
    return render_template('about.html', user_status = user_status, all_motions = all_motions)
    
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
    # if Motion.query.filter_by(author_id = session['user_id']).all() != []:
        # return redirect(url_for('scoring'))
    categories = db.session.query(Topic.category).distinct()
    motions = Topic.query.all()
    user_position = False
    if request.method == 'POST' and len(request.form['abstract']) == 0 and len(request.form['abstract1']) == 0:
        if request.form['category_value'] == "all":
            motions = Topic.query.distinct(Topic.category).all()
            category_header = "All"
        else:
            motions = Topic.query.filter_by(category = request.form['category_value'])
            category_header = str(request.form['category_value'])
        return render_template('arguments2.html', categories=categories, motions=motions, category_header = category_header)        
    if request.method == 'POST' and len(request.form['abstract']) >= 0 and len(request.form['abstract1']) >= 0:
        topic_id = db.session.query(Topic).filter_by(topic = request.form['motion_value']).all()[0]
        if request.form['user_stance'] == "pro":
            added_motion = Motion(topic_id.id, session['user_id'], True)
            db.session.add(added_motion)
        else:
            added_motion = Motion(topic_id.id, session['user_id'], False)
            db.session.add(added_motion)
        pro_argument = ProArgument(request.form['abstract'], request.form['argument'], session['user_id'], added_motion.id)
        con_argument = ConArgument(request.form['abstract1'], request.form['argument1'], session['user_id'], added_motion.id)
        db.session.add(pro_argument)
        db.session.add(con_argument)
        db.session.commit()
        return redirect(url_for('voting'))
    return render_template('arguments2.html', categories=categories, motions=motions)
    
@app.route('/voting/<string:topic_number>', methods=['GET','POST'])
@login_required    
def voting(topic_number):
    user_motions = db.session.query(Motion).filter_by(topic_id = topic_number, user_id = session['user_id']).all()
    if user_motions == []:
        flash('You need to submit arguments before you can vote!')
        return redirect(url_for('add_arguments'))
    all_other_motions = db.session.query(Motion)
    other_motions = [int(motion.topic_id) for motion in all_other_motions if motion.topic_id != int(topic_number) if motion.user_id == session['user_id']]
    other_topics = db.session.query(Topic).filter(Topic.id.in_(other_motions)).all()
    other_categories = db.session.query(Topic.category).distinct()
    user_available_motions = [{} for x in xrange(len(list(other_categories)))]
    for index, cat in enumerate(other_categories):
        temp_list = []
        for top in other_topics:
            if str(cat[0]) == str(top.category):
                temp_list.append(top)
            else:
                pass
        user_available_motions[index][str(cat[0])] = temp_list   
    other_user_motions = [i for i in user_available_motions if i.values()[0] != []]
    if request.method == 'POST':
        argument_ids = session['argument_ids']
        motion_ids = session['motion_ids']
        votes = request.form.getlist('vote_value')
        for position, vote in enumerate(votes):
            if session['user_status'] == True:
                vote_record = ProVote(argument_ids[position], motion_ids[position], int(vote), int(session['user_id']))
            else:
                vote_record = ConVote(argument_ids[position], motion_ids[position], int(vote), int(session['user_id']))
            db.session.add(vote_record)
        db.session.commit()
    other_users = db.session.query(Motion.id).filter_by(topic_id = topic_number).all()
    other_motion_ids = tuple(motion[0] for motion in other_users)
    if user_motions[0].user_procon == True:
        session['user_status'] = True
        displayable_arguments = db.session.query(ProArgument).filter(ProArgument.motion_id.in_(other_motion_ids)).all()
    else:
        session['user_status'] = False
        displayable_arguments = db.session.query(ConArgument).filter(ConArgument.motion_id.in_(other_motion_ids)).all()
    userless_arguments = [argument for argument in displayable_arguments if argument.author_id != session['user_id']]  
    arguments = random.sample(userless_arguments, 4)
    topic = db.session.query(Topic).filter_by(id = topic_number)[0]
    session['argument_ids'] = [argument.id for argument in arguments]
    session['motion_ids'] = [argument.motion_id for argument in arguments]
    user_status = session['user_status']
    return render_template("index.html", user_status=user_status, arguments=arguments, topic=topic, other_user_motions=other_user_motions)

    
@app.route('/scoring/<string:topic_number>', methods=['GET'])
@login_required    
def scoring(topic_number):
    user_motion = db.session.query(Motion).filter_by(topic_id = topic_number, user_id = session['user_id']).all()
    if user_motion == []:
        flash('You need to submit arguments for this motion in order to have scores!')
        return redirect(url_for('add_arguments'))
    user_motion = user_motion[0]
    current_topic = db.session.query(Topic).filter_by(id = int(topic_number)).all()[0]
    user_proargument = db.session.query(ProArgument).filter_by(id = user_motion.id).all()[0]
    user_proargument_votes = db.session.query(func.count(ProVote.id)).filter_by(argument_id = user_motion.id).all()[0][0]
    if user_proargument_votes == 0:
        user_proargument_avgvotes = 0
    else:
        user_proargument_avgvotes = round(db.session.query(func.avg(ProVote.value)).filter_by(argument_id = user_motion.id).all()[0][0], 1)
    user_conargument = db.session.query(ConArgument).filter_by(id = user_motion.id).all()[0]
    user_conargument_votes = db.session.query(func.count(ConVote.id)).filter_by(argument_id = user_motion.id).all()[0][0]
    if user_conargument_votes == 0:
        user_conargument_avgvotes = 0
    else:
        user_conargument_avgvotes = round(db.session.query(func.avg(ConVote.value)).filter_by(argument_id = user_motion.id).all()[0][0], 1)
    other_motions = db.session.query(Motion).filter_by(topic_id = topic_number).all()
    if user_motion.user_procon == True:
        user_position = "for"
        other_motions = [motion.id for motion in other_motions if motion.user_id != session['user_id'] and motion.user_procon == False]
        other_turing_votes = db.session.query(func.count(ProVote.id)).filter(ProVote.argument_id.in_(other_motions)).all()[0][0]
        other_turing_avgvotes = db.session.query(ProVote.argument_id, func.avg(ProVote.value)).filter(ProVote.argument_id.in_(other_motions)).group_by(ProVote.argument_id).all()
        try:
            percentile_ranking = str(round((float(len([avg for avg in other_turing_avgvotes if round(avg[1], 2) < round(user_conargument_avgvotes, 2)])) / len(other_turing_avgvotes))*100, 1)) + "%"
        except ZeroDivisionError:
            percentile_ranking = "0% (no votes yet)"
    else:
        user_position = "against"
        other_motions = [motion.id for motion in other_motions if motion.user_id != session['user_id'] and motion.user_procon == True]
        other_turing_votes = db.session.query(func.count(ConVote.id)).filter(ConVote.argument_id.in_(other_motions)).all()[0][0]
        other_turing_avgvotes = db.session.query(ConVote.argument_id, func.avg(ConVote.value)).filter(ConVote.argument_id.in_(other_motions)).group_by(ConVote.argument_id).all()
        try:
            percentile_ranking = str(round((float(len([avg for avg in other_turing_avgvotes if round(avg[1], 2) < round(user_proargument_avgvotes, 2)])) / len(other_turing_avgvotes))*100, 1)) + "%"
        except ZeroDivisionError:
            percentile_ranking = "0% (no votes yet)"
    all_other_motions = db.session.query(Motion)
    other_motions = [int(motion.topic_id) for motion in all_other_motions if motion.topic_id != int(topic_number) if motion.user_id == session['user_id']]
    other_topics = db.session.query(Topic).filter(Topic.id.in_(other_motions)).all()
    other_categories = db.session.query(Topic.category).distinct()
    user_available_motions = [{} for x in xrange(len(list(other_categories)))]
    for index, cat in enumerate(other_categories):
        temp_list = []
        for top in other_topics:
            if str(cat[0]) == str(top.category):
                temp_list.append(top)
            else:
                pass
        user_available_motions[index][str(cat[0])] = temp_list   
    other_user_motions = [i for i in user_available_motions if i.values()[0] != []]
    return render_template("scoring.html",
        current_topic=current_topic,
        user_position=user_position,
        user_proargument=user_proargument,
        user_proargument_votes=user_proargument_votes,
        user_proargument_avgvotes=user_proargument_avgvotes,
        user_conargument=user_conargument,
        user_conargument_votes=user_conargument_votes,
        user_conargument_avgvotes=user_conargument_avgvotes,
        other_turing_votes=other_turing_votes,
        percentile_ranking=percentile_ranking,
        other_user_motions=other_user_motions
           )
    
    
# @app.route('/scoring', methods=['GET'])
# @login_required    
# def scoring():
    # user_pro_argument = db.session.query(ArgumentPost).filter_by(author_id = session['user_id'], procon_topic=True).all()[0]
    # user_con_argument = db.session.query(ArgumentPost).filter_by(author_id = session['user_id'], procon_topic=False).all()[0]
    # user_pro_votes = db.session.query(func.count(Vote.value)).filter_by(argument_id = user_pro_argument.id)[0][0]
    # user_pro_score = round(float(db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_pro_argument.id)[0][0]), 1) if db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_pro_argument.id)[0][0] is not None else 0
    # user_con_votes = db.session.query(func.count(Vote.value)).filter_by(argument_id = user_con_argument.id)[0][0]
    # user_con_score = round(float(db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_con_argument.id)[0][0]), 1) if db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_con_argument.id)[0][0] is not None else 0
    # user_total_votes = user_pro_votes + user_con_votes
    # user_position = None
    # if user_pro_argument.user_procon == True:
        # user_position = True    
        # opposite_total_votes = db.session.query(func.count(Vote.value)).join(ArgumentPost, Vote.argument_id == ArgumentPost.id).filter_by(procon_topic = True, user_procon = False).all()[0][0]
        # opposite_average_score = round(float(db.session.query(func.avg(Vote.value)).join(ArgumentPost, Vote.argument_id == ArgumentPost.id).filter_by(procon_topic = True, user_procon = False).all()[0][0]), 1) if db.session.query(func.avg(Vote.value)).join(ArgumentPost, Vote.argument_id == ArgumentPost.id).filter_by(procon_topic = True, user_procon = False).all()[0][0] is not None else 0
    # else:
        # opposite_total_votes = db.session.query(func.count(Vote.value)).join(ArgumentPost, Vote.argument_id == ArgumentPost.id).filter_by(procon_topic = False, user_procon = True).all()[0][0]
        # opposite_average_score = round(float(db.session.query(func.avg(Vote.value)).join(ArgumentPost, Vote.argument_id == ArgumentPost.id).filter_by(procon_topic = False, user_procon = True).all()[0][0]), 1) if db.session.query(func.avg(Vote.value)).join(ArgumentPost, Vote.argument_id == ArgumentPost.id).filter_by(procon_topic = False, user_procon = True).all()[0][0] is not None else 0
        # opposite_total_votes = db.session.execute("SELECT COUNT(votes.value) FROM votes JOIN arguments ON votes.argument_id = arguments.id WHERE arguments.procon_topic = 0 AND arguments.user_procon = 1")
        # opposite_average_score = db.session.execute("SELECT AVG(votes.value) FROM votes JOIN arguments ON votes.argument_id = arguments.id WHERE arguments.procon_topic = 0 AND arguments.user_procon = 1")   
    # return render_template("scoring.html", 
        # user_position = user_position, 
        # user_pro_argument = user_pro_argument, 
        # user_con_argument = user_con_argument,
        # user_pro_votes = user_pro_votes,
        # user_con_votes = user_con_votes,
        # user_pro_score = user_pro_score,
        # user_con_score = user_con_score,
        # user_total_votes = user_total_votes,
        # opposite_total_votes = opposite_total_votes,
        # opposite_average_score = opposite_average_score
           # )
    
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
    return redirect(url_for('home'))    
 
if __name__ == '__main__':
    app.run(debug=True)
