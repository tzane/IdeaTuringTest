from flask import Flask, render_template, redirect, url_for, request, session, flash, g, send_from_directory, jsonify
from flask_restful import reqparse
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from functools import wraps
from forms import LoginForm, RegisterForm
from sqlalchemy.sql import func, expression
from sqlalchemy.orm import aliased
from numpy import average, std
import random
from operator import itemgetter
import datetime
# import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

import os

app.secret_key = "my precious"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arguments.db'

# create the sqlalchemy object
db = SQLAlchemy(app)

from models import *

@app.route('/')
def home():
    update_topic_status()
    all_topics = db.session.query(Topic).filter_by(status = True).all()
    other_categories = db.session.query(Topic.category).distinct()
    user_available_motions = [{} for x in xrange(len(list(other_categories)))]
    for index, cat in enumerate(other_categories):
        temp_list = []
        for top in all_topics:
            if str(cat[0]) == str(top.category):
                temp_list.append(top)
            else:
                pass
        user_available_motions[index][cat[0]] = temp_list    
    all_motions = [i for i in user_available_motions if i.values()[0] != []]
    user_status = None

    try:
        if session['logged_in'] == True:
            user_status = True
    except KeyError:
        return render_template('about.html', user_status = user_status, all_motions = all_motions)
    
    user_topics = db.session.query(Topic.id).distinct().join(Motion).filter(Motion.user_id == session['user_id'])
    user_topics = [top[0] for top in user_topics]
    randnum = random.sample(user_topics, 1)[0]
    return render_template('about.html', user_status = user_status, all_motions = all_motions, randnum = randnum)
    
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
    
@app.route('/proposetopic', methods=['GET'])
@login_required
def get_proposed_topic():
    categories = db.session.query(Topic.category).distinct()  
    return render_template('add_topic.html', categories=categories)
    
@app.route('/proposetopic', methods=['POST'])
@login_required
def add_proposed_topic():
    proposed_topic = ProposedTopic(request.form['category_value'], request.form['topic'], session['user_id'])
    db.session.add(proposed_topic)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/votemotion/<int:topic_number>', methods=['GET'])
@login_required
def show_proposed_topic(topic_number):
    proposed_topic = ProposedTopic.query.get(topic_number)
    if proposed_topic == None:
        flash('This proposed motion doesn\'t exist.')
        return redirect(url_for('home'))
    current_user_query = db.session.query(ProposedTopicVote).filter_by(proposedtopic_id = topic_number)
    current_user = [vote.vote_value for vote in current_user_query if vote.author_id == session['user_id']]
    user_comment = db.session.query(ProposedTopicComment).filter_by(proposedtopic_id = topic_number, author_id = session['user_id'])
    user_comment = [com.comment for com in user_comment]
    up_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = True, proposedtopic_id = topic_number)
    up_votes = up_votes[0][0]
    down_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = False, proposedtopic_id = topic_number)
    down_votes = down_votes[0][0]
    
    comments_query = db.session.query(User, ProposedTopicComment).join(ProposedTopicComment).filter_by(proposedtopic_id = topic_number).order_by(ProposedTopicComment.created_datetime.desc()).all()
    number_comments = db.session.query(func.count(ProposedTopicComment.id)).filter(ProposedTopicComment.proposedtopic_id == topic_number).all()[0][0]
    
    return render_template('vote_topic.html', 
        proposed_topic=proposed_topic, 
        current_user=current_user, 
        user_comment=user_comment, 
        up_votes=up_votes,
        down_votes=down_votes,
        number_comments=number_comments,
        comments_query=comments_query)

@app.route('/votemotion/<int:topic_number>', methods=['POST'])
@login_required
def vote_proposed_topic(topic_number):
    url = "/votemotion/{interger}".format(interger = topic_number)
    
    vote_value = request.form.get('user_vote')
    if vote_value == None:
        # Didn't submit a vote
        # Find a way to flash notification?
        return redirect(url)
    vote_update = db.session.query(ProposedTopicVote).filter_by(proposedtopic_id = topic_number, author_id=session['user_id']).all()
    new_vote = True if vote_value == 'true' else False
    if vote_update == []:
        db.session.add(ProposedTopicVote(new_vote, topic_number, session['user_id']))
        db.session.commit()
    else:
        vote_update[0].vote_value = new_vote
        db.session.commit()
    
    comment = request.form['comment']
    comment_update = db.session.query(ProposedTopicComment).filter_by(proposedtopic_id = topic_number, author_id = session['user_id']).all()
    if comment == "":
        pass
    else:
        if comment_update == []:
            db.session.add(ProposedTopicComment(comment, topic_number, session['user_id']))
            db.session.commit()
        else:
            comment_update[0].comment = comment
            comment_update[0].created_datetime = datetime.datetime.now()
            db.session.commit()
    
    db.session.commit()
    return redirect(url)      
    
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

@app.route('/arguments', methods=['POST'])
@login_required
def add_arguments():
    topic_id = db.session.query(Topic).filter_by(topic = request.form['motion_value'], status = True).all()[0]
    if request.form['user_stance'] == "pro":
        added_motion = Motion(topic_id.id, session['user_id'], True)
        db.session.add(added_motion)
    else:
        added_motion = Motion(topic_id.id, session['user_id'], False)
        db.session.add(added_motion)   
    motion_id = db.session.query(Motion.id).order_by(Motion.id.desc()).first()[0]
    pro_argument = Argument(True, request.form['abstract'], request.form['argument'], session['user_id'], motion_id)
    con_argument = Argument(False, request.form['abstract1'], request.form['argument1'], session['user_id'], motion_id)
    db.session.add(pro_argument)
    db.session.add(con_argument)
    db.session.commit()
    
    flash("You just submitted your arguments which other users will vote on. Now go vote on theirs and earn some credits back!")
    url = "/voting/{interger}".format(interger = topic_id.id)
    return redirect(url)
 
@app.route('/arguments', methods=['GET'])
@login_required
def get_arguments():
    update_topic_status()
    category_filter = request.args.get('category_value', 'all')
    categories = db.session.query(Topic.category).distinct()
    if category_filter == 'all':
        motions = Topic.query.distinct(Topic.category).filter_by(status = True).all()
        category_header = "All"
    else:
        motions = Topic.query.filter_by(category = category_filter, status = True)
        category_header = category_filter
    topics = db.session.query(func.count(Topic.id)).filter_by(status = True).all()[0][0]
    randnum = random.choice(range(1, topics + 1))
    return render_template('arguments.html', category_header = category_header, categories=categories, motions=motions, randnum=randnum)
    
@app.route('/voting/<int:topic_number>', methods=['GET','POST'])
@login_required    
def voting(topic_number):
    user_motion = db.session.query(Motion).filter_by(topic_id = topic_number, user_id = session['user_id']).all()
    if user_motion == []:
        flash('You need to submit arguments before you can vote!')
        return redirect(url_for('add_arguments'))
    update_topic_status()
    other_topics = Topic.query.join(Motion, User).filter(Motion.topic_id != topic_number, User.id == session['user_id']).all()
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
            vote_record = Vote(argument_ids[position], motion_ids[position], int(vote), int(session['user_id']))
            db.session.add(vote_record)
        db.session.commit()
    other_users = db.session.query(Motion.id).filter_by(topic_id = topic_number).all()
    other_motion_ids = tuple(motion[0] for motion in other_users)
    if user_motion[0].user_procon == True:
        session['user_status'] = True
        displayable_arguments = Argument.query.join(Motion, Topic).filter(Argument.procon == True, Topic.id == topic_number, Topic.status == True).all()
    else:
        session['user_status'] = False
        displayable_arguments = Argument.query.join(Motion, Topic).filter(Argument.procon == False, Topic.id == topic_number, Topic.status == True).all() 
    displayable_arguments = [arg for arg in displayable_arguments if arg.author_id != session['user_id']]
    try:
        arguments = random.sample(displayable_arguments, 4)
    except ValueError:
        # flash messages
        return "new url for topic with enough args to vote on"    
    topic = db.session.query(Topic).filter_by(id = topic_number)[0]
    session['argument_ids'] = [argument.id for argument in arguments]
    session['motion_ids'] = [argument.motion_id for argument in arguments]
    user_status = session['user_status']
    topics = db.session.query(func.count(Topic.id)).filter_by(status = True).all()[0][0]
    randnum = random.choice(range(1, topics + 1))
    return render_template("index.html", user_status=user_status, arguments=arguments, topic=topic, other_user_motions=other_user_motions, randnum=randnum)

    
@app.route('/scoring/<int:topic_id>', methods=['GET'])
@login_required    
def scoring(topic_id):
    user_motion = db.session.query(Motion).filter_by(topic_id = topic_id, user_id = session['user_id']).all()
    user_proargument = Argument.query.join(Motion, User).filter(Motion.topic_id == topic_id, User.id == session['user_id'], Argument.procon == True).all()[0]
    user_proargument_votes = db.session.query(func.count(Vote.id)).filter_by(argument_id = user_proargument.id).all()[0][0]
    user_proargument_avgvotes = round(db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_proargument.id).all()[0][0], 1) if user_proargument_votes > 0 else 0
    user_conargument = Argument.query.join(Motion, User).filter(Motion.topic_id == topic_id, User.id == session['user_id'], Argument.procon == False).all()[0]
    user_conargument_votes = db.session.query(func.count(Vote.id)).filter_by(argument_id = user_conargument.id).all()[0][0]
    user_conargument_avgvotes = round(db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_conargument.id).all()[0][0], 1) if user_conargument_votes > 0 else 0
        
    if user_motion == []:
        flash('You need to submit arguments for this motion in order to have scores!')
        return redirect(url_for('add_arguments'))
        
    user_motion = user_motion[0]
  
    if user_motion.user_procon == True:
        user_turing_argument = db.session.query(Argument.id).filter_by(motion_id = user_motion.id, procon = False)
        user_position = "for"
        opposite_arguments = Argument.query.join(Motion, User).filter(Motion.topic_id == topic_id, User.id != session['user_id'], Motion.user_procon == False, Argument.procon == True).all()
    else:
        user_turing_argument = db.session.query(Argument.id).filter_by(motion_id = user_motion.id, procon = True)
        user_position = "against"
        opposite_arguments = Argument.query.join(Motion, User).filter(Motion.topic_id == topic_id, User.id != session['user_id'], Motion.user_procon == True, Argument.procon == False).all()
        
    opposite_argument_ids = [argument.id for argument in opposite_arguments]
    other_turing_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id.in_(opposite_argument_ids)).all()[0][0]
    user_turing_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id.in_(user_turing_argument))[0][0]
    user_turing_score = round(db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(user_turing_argument))[0][0], 1) if user_turing_votes > 0 else 0
    opposite_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id.in_(opposite_argument_ids))[0][0]
    opposite_avgvotes = db.session.query(Vote.argument_id, func.avg(Vote.value)).filter(Vote.argument_id.in_(opposite_argument_ids)).group_by(Vote.argument_id)
    percentile_ranking = round((len([avgvote[1] for avgvote in opposite_avgvotes if round(avgvote[1], 2) < round(user_turing_score, 2)]) / len([avgvote[1] for avgvote in opposite_avgvotes]))*100, 1) if opposite_votes > 0 else 0
    opp_lower_bound = round(average([i[1] for i in opposite_avgvotes]) - std([i[1] for i in opposite_avgvotes]), 1) if opposite_votes > 0 else 0
    opp_upper_bound = round(std([i[1] for i in opposite_avgvotes]) + average([i[1] for i in opposite_avgvotes]), 1) if opposite_votes > 0 else 0
  
    current_topic = Topic.query.get(topic_id)
    
    update_topic_status()
    other_topics = Topic.query.join(Motion, User).filter(Motion.topic_id != topic_id, User.id == session['user_id']).all()
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
    
    user_topics = db.session.query(Topic.id).join(Motion).filter(Motion.user_id == session['user_id'], Topic.status == True)
    user_topics = [top[0] for top in user_topics]
    randnum = random.sample(user_topics, 1)[0]
    
    return render_template("scoring.html",
        current_topic=current_topic,
        user_position=user_position,
        user_proargument=user_proargument,
        user_proargument_votes=user_proargument_votes,
        user_proargument_avgvotes=user_proargument_avgvotes,
        user_conargument=user_conargument,
        user_conargument_votes=user_conargument_votes,
        user_conargument_avgvotes=user_conargument_avgvotes,
        opp_lower_bound=opp_lower_bound,
        opp_upper_bound=opp_upper_bound,
        other_turing_votes=other_turing_votes,
        percentile_ranking=percentile_ranking,
        other_user_motions=other_user_motions,
        randnum=randnum
        )
        
       
@app.route('/turingarguments/topic/<int:topic_id>/topscoring', methods=['GET'])
def top_turing_args(topic_id):
    current_topic = Topic.query.get(topic_id)    

    con_mots = db.session.query(Motion.id).filter(Motion.topic_id == topic_id, Motion.user_procon == False).all()
    pro_mots = db.session.query(Motion.id).filter(Motion.topic_id == topic_id, Motion.user_procon == True).all()
    con_motion_ids = [mot[0] for mot in con_mots]
    pro_motion_ids = [mot[0] for mot in pro_mots]
    con_args = db.session.query(Argument.id).join(Motion).filter(Motion.id.in_(con_motion_ids), Argument.procon == True).all()
    pro_args = db.session.query(Argument.id).join(Motion).filter(Motion.id.in_(pro_motion_ids), Argument.procon == False).all()
    con_arg_ids = [arg[0] for arg in con_args]
    pro_arg_ids = [arg[0] for arg in pro_args]
    con_arguments = db.session.query(func.avg(Vote.value), Argument.id).join(Argument).filter(Argument.id.in_(con_arg_ids)).group_by(Argument.id)
    pro_arguments = db.session.query(func.avg(Vote.value), Argument.id).join(Argument).filter(Argument.id.in_(pro_arg_ids)).group_by(Argument.id)
    
    rank = request.args.get('ranking')
    if rank is None:
        rank = 1
    
    max_pro_args = sorted(pro_arguments, key=itemgetter(0), reverse=True)[:int(rank)]
    max_con_args = sorted(con_arguments, key=itemgetter(0), reverse=True)[:int(rank)]
    
    pro_args = []
    con_args = []
    
    if len(max_pro_args) > len(max_con_args):
        iterations = len(max_con_args)
    else:
        iterations = len(max_pro_args)
    # FIX THIS    
    if int(rank) > int(iterations):
        print "blah!"
        url = "/turingarguments/topic/{topic}/topscoring?ranking={number}".format(topic = topic_id, number = iterations)
        return redirect(url)
            
    for index in list(range(0, iterations)):
        pro_ranking = index + 1
        pro_votes = db.session.query(func.count(Vote.id)).join(Motion, Argument).filter(Argument.id == max_pro_args[index][1])[0][0]
        pro_avg_votes = round(max_pro_args[index][0], 1)
        pro_args.append((pro_ranking, Argument.query.get(max_pro_args[index][1]), pro_votes, pro_avg_votes))
        con_ranking = index + 1
        con_votes = db.session.query(func.count(Vote.id)).join(Motion, Argument).filter(Argument.id == max_con_args[index][1])[0][0]
        con_avg_votes = round(max_con_args[index][0], 1)
        con_args.append((con_ranking, Argument.query.get(max_con_args[index][1]), con_votes, con_avg_votes))
        
    update_topic_status()
    other_topics = Topic.query.join(Motion, User).filter(Motion.topic_id != topic_id, User.id == session['user_id']).all()
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
    
    topics = db.session.query(func.count(Topic.id)).filter_by(status = True)[0][0]
    randnum = random.choice(range(1, topics + 1))
    
    user_topics = db.session.query(Topic.id).join(Motion).filter(Motion.user_id == session['user_id'])
    user_topics = [top[0] for top in user_topics]
    user_randtop = random.sample(user_topics, 1)[0]
    
    return render_template("top_args.html",
        current_topic=current_topic,
        con_args=con_args,
        pro_args=pro_args,
        ranking=iterations,
        other_user_motions = other_user_motions,
        randnum=randnum,
        user_randtop = user_randtop
        )    
    
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

def update_topic_status():
    active_topics = db.session.query(Topic).filter_by(status = True).all()
    for topic in active_topics:
        if "Closed" in topic.days_left():
            updated_topic = Topic.query.get(topic.id)
            updated_topic.status = False
            db.session.commit()
 
if __name__ == '__main__':
    app.run(debug=True)
