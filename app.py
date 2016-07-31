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
    user_topics = db.session.query(Topic.id).distinct().join(Motion).filter(Motion.user_id == session['user_id'])
    user_topics = [top[0] for top in user_topics]
    randnum = random.sample(user_topics, 1)[0]
    user_points = get_user_points()
    proposed_topics = db.session.query(ProposedTopic.id).distinct()
    proposed_topics = [prop[0] for prop in proposed_topics]
    randProposedTopic = random.sample(proposed_topics, 1)[0]
    return render_template('about.html', user_points = user_points, all_motions = all_motions, randnum = randnum, randProposedTopic = randProposedTopic)
    
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
    
@app.route('/propose-motion', methods=['GET'])
@login_required
def get_proposed_topic():
    categories = db.session.query(Topic.category).distinct()
    user_points = get_user_points()    
    return render_template('add_topic.html', categories=categories, user_points = user_points)
    
@app.route('/propose-motion', methods=['POST'])
@login_required
def add_proposed_topic():
    points = get_user_points()
    closed_topics = db.session.query(Topic.id).filter_by(status = False).all()
    closed_topics = [elem[0] for elem in closed_topics]
    votes_per_topic = db.session.query(Motion.topic_id, func.count(Vote.id)).join(Vote).filter(~ Motion.topic_id.in_(closed_topics), Vote.voter_id == session['user_id']).group_by(Motion.topic_id).all()
    if points < 30:
        flash("You don't have enough points! You need to earn more by voting more arguments.")
        return redirect(url_for('add_proposed_topic'))
    for tuple in votes_per_topic:
        if tuple[1] < 9:
            message = "You need to vote on arguments at least 9 times for every new debate you enter before proposing your own. You need to vote {integer} more times on this issue.".format(integer = 9 - tuple[1])
            url = "/voting/{interger}".format(interger = tuple[0])
            flash(message)
            return redirect(url)      
    if request.form['topic'] == '':
        flash("You didn't submit anything!")
        return redirect(url_for('add_proposed_topic'))
    proposed_topic = ProposedTopic(request.form['category_value'], request.form['topic'], session['user_id'])
    db.session.add(proposed_topic)
    user = User.query.filter_by(id=session['user_id'])
    user[0].points -= 30
    db.session.commit()
    return redirect(url_for('home'))
    
@app.route('/edit-motion/<int:topic_number>', methods=['GET'])
@login_required
def get_edited_proposed_topic(topic_number):
    categories = db.session.query(Topic.category).distinct()
    motion_update = ProposedTopic.query.get(topic_number)  
    return render_template('edit_topic.html', motion_update=motion_update, categories=categories)
    
    
@app.route('/edit-motion/<int:topic_number>', methods=['POST'])
@login_required
def add_edited_proposed_topic(topic_number):
    motion_update = ProposedTopic.query.get(topic_number)
    motion_update.category = request.form['category_value']
    motion_update.topic = request.form['topic']
    motion_update.created_date = datetime.date.today()
    db.session.commit()
    url = "/vote-motion/{interger}".format(interger = topic_number)
    return redirect(url)

@app.route('/vote-motion/<int:topic_number>', methods=['GET'])
@login_required
def show_proposed_topic(topic_number):
    proposed_topic = ProposedTopic.query.get(topic_number)
    if proposed_topic == None:
        flash('The proposed motion you\'re trying to vote for doesn\'t exist.')
        return redirect(url_for('home'))
    if proposed_topic.author_id == session['user_id']:
        user_proposed = True
    else:
        user_proposed = False
    current_user_query = db.session.query(ProposedTopicVote).filter_by(proposedtopic_id = topic_number)
    current_user = [vote.vote_value for vote in current_user_query if vote.author_id == session['user_id']]
    user_comment = db.session.query(ProposedTopicComment).filter_by(proposedtopic_id = topic_number, author_id = session['user_id'])
    user_comment = [com.comment for com in user_comment]
    up_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = True, proposedtopic_id = topic_number)
    up_votes = up_votes[0][0]
    down_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = False, proposedtopic_id = topic_number)
    down_votes = down_votes[0][0]
    
    total_users = db.session.query(func.count(User.id))
    total_users = total_users[0][0]
    up_vote_share = round(float(up_votes) / float(total_users), 2)
    
    if total_users <= 5:
        if up_votes < 3:
            votes_needed = 3 - up_votes
    elif total_users > 5 and total_users <= 10:
        if up_votes < 4:
            votes_needed = 4 - up_votes
    elif total_users > 10 and total_users <= 25:
        if up_votes < 5:
            votes_needed = 5 - up_votes
    elif total_users > 25 and total_users <= 100:
        if vote_share < 0.15:
            necessary_votes = int(round(0.15 * total_users, 0))
            votes_needed = necessary_votes - up_votes
    elif total_users > 100 and total_users <= 500:
        if vote_share < 0.10:
            necessary_votes = int(round(0.10 * total_users, 0))
            votes_needed = necessary_votes - up_votes
    elif total_users > 500:
        if vote_share < 0.05:
            necessary_votes = int(round(0.05 * total_users, 0))
            votes_needed = necessary_votes - up_votes  
    else:
        pass
    
    comments_query = db.session.query(User, ProposedTopicComment).join(ProposedTopicComment).filter_by(proposedtopic_id = topic_number).order_by(ProposedTopicComment.created_datetime.desc()).all()
    other_propTopics = ProposedTopic.query.filter(ProposedTopic.id != topic_number, User.id == session['user_id']).all()
    other_propCategories = db.session.query(ProposedTopic.category).distinct()
    user_available_propTopics = [{} for x in xrange(len(list(other_propCategories)))]
    for index, cat in enumerate(other_propCategories):
        temp_list = []
        for top in other_propTopics:
            if str(cat[0]) == str(top.category):
                temp_list.append(top)
                user_voted = db.session.query(ProposedTopicVote.id).filter_by(proposedtopic_id = top.id, author_id = session['user_id']).all()
                if user_voted == []:
                    temp_list.append("**You haven\'t voted on this**")
            else:
                pass
        user_available_propTopics[index][str(cat[0])] = [temp_list]     
    other_prop_topics = [i for i in user_available_propTopics if i.values()[0] != [[]]]
    
    return render_template('vote_topic.html',
        user_proposed=user_proposed,    
        proposed_topic=proposed_topic, 
        current_user=current_user, 
        user_comment=user_comment, 
        up_votes=up_votes,
        down_votes=down_votes,
        comments_query=comments_query,
        votes_needed=votes_needed,
        other_prop_topics=other_prop_topics)        

@app.route('/vote-motion/<int:topic_number>', methods=['POST'])
@login_required
def vote_proposed_topic(topic_number):
    url = "/vote-motion/{interger}".format(interger = topic_number)
    
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
    
    up_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = True, proposedtopic_id = topic_number)
    up_votes = up_votes[0][0]
    total_users = db.session.query(func.count(User.id))
    total_users = total_users[0][0]
    up_vote_share = round(float(up_votes) / float(total_users), 2)
    
    activated_motion_url = "/arguments"
    
    if total_users <= 5:
        if up_votes >= 3:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is not active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 5 and total_users <= 10:
        if up_votes >= 4:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is not active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 10 and total_users <= 25:
        if up_votes >= 5:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is not active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 25 and total_users <= 100:
        if vote_share > 0.15:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is not active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 100 and total_users <= 500:
        if vote_share > 0.10:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is not active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 500:
        if vote_share > 0.05:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is not active for debate. Add your arguments!')
            return redirect(activated_motion_url)            
    else:
        pass
    
    db.session.commit()
    return redirect(url) 

def activate_proposed_motion(integer):
    proposed_motion = ProposedTopic.query.get(integer)
    db.session.add(Topic(proposed_motion.category, proposed_motion.topic, proposed_motion.author_id, True))
    db.session.delete(proposed_motion)
    db.session.commit()    
    
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
    forms = [request.form['abstract'], request.form['argument'], request.form['abstract1'], request.form['argument1']]
    if '' in forms:
       flash("You need to submit something for all the required fields!")
       return redirect(url_for('add_arguments'))
    
    closed_topics = db.session.query(Topic.id).filter_by(status = False).all()
    closed_topics = [elem[0] for elem in closed_topics]
    votes_per_topic = db.session.query(Motion.topic_id, func.count(Vote.id)).join(Vote).filter(~ Motion.topic_id.in_(closed_topics), Vote.voter_id == session['user_id']).group_by(Motion.topic_id).all()
    points = get_user_points()
    if points < 15:
       flash("You don't have enough points! You need to earn more by voting more arguments.")
       return redirect(url_for('arguments'))
    
    for tuple in votes_per_topic:
       if tuple[1] < 9:
          message = "You need to vote on arguments at least 9 times for every new debate you enter before proposing your own. You need to vote {integer} more times on this issue.".format(integer = 9 - tuple[1])
          url = "/voting/{interger}".format(interger = tuple[0])
          flash(message)
          return redirect(url)
              
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
    
    user = User.query.filter_by(id=session['user_id'])
    user[0].points -= 15
    
    db.session.commit()
    
    flash("You just submitted your arguments which other users will vote on. Now go vote on theirs and earn some credits back!")
    url = "/voting/{interger}".format(interger = topic_id.id)
    return redirect(url)
 
@app.route('/arguments', methods=['GET'])
@login_required
def get_arguments():
    user_points = get_user_points()
    update_topic_status()
    category_filter = request.args.get('category_value', 'all')
    categories = db.session.query(Topic.category).distinct()
    user_motions = Motion.query.filter_by(user_id = session['user_id']).all()
    user_topics = [motion.topic_id for motion in user_motions]
    if category_filter == 'all':
        motions = db.session.query(Topic).filter(~ Topic.id.in_(user_topics), Topic.status == True)
        category_header = "All"
    else:
        motions = db.session.query(Topic).filter(~ Topic.id.in_(user_topics), Topic.category == category_filter, Topic.status == True)
        category_header = category_filter
    topics = db.session.query(func.count(Topic.id)).filter_by(status = True).all()[0][0]
    randnum = random.choice(range(1, topics + 1))
    return render_template('arguments.html', category_header = category_header, categories=categories, motions=motions, randnum=randnum, user_points=user_points)
    
@app.route('/voting/<int:topic_number>', methods=['GET','POST'])
@login_required    
def voting(topic_number):
    user_motion = db.session.query(Motion).filter_by(topic_id = topic_number, user_id = session['user_id']).all()
    user_points = get_user_points()
    user = User.query.filter_by(id=session['user_id'])
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
            comment_field = request.form.get('comment' + str(argument_ids[position]), None)
            if comment_field == None or comment_field == "":
                pass
            else:
                user_comment = db.session.query(ArgumentComment).filter_by(argument_id = argument_ids[position], author_id = session['user_id']).all()
                if user_comment == []:
                    db.session.add(ArgumentComment(comment_field, argument_ids[position], session['user_id']))
                else:
                    user_comment[0].comment = comment_field
                    user_comment[0].created_datetime = datetime.datetime.now()
        user[0].points += 3
        db.session.commit()
    if user_motion[0].user_procon == True:
        session['user_status'] = True
        displayable_arguments = Argument.query.join(Motion, Topic).filter(Argument.procon == True, Topic.id == topic_number, Topic.status == True).all()
    else:
        session['user_status'] = False
        displayable_arguments = Argument.query.join(Motion, Topic).filter(Argument.procon == False, Topic.id == topic_number, Topic.status == True).all()  
    displayable_arguments = [arg for arg in displayable_arguments if arg.author_id != session['user_id']]
    arguments = displayable_arguments
    try:
        arguments = random.sample(displayable_arguments, 3)
    except ValueError:
        # not enough arguments submitted to vote on (4 minimum)
        flash("There\'s not enough arguments to vote on for this motion. Check back soon!")
        return redirect(url_for('home'))
    topic = db.session.query(Topic).filter_by(id = topic_number)[0]
    session['argument_ids'] = [argument.id for argument in arguments]
    comments_query = db.session.query(User, ArgumentComment).join(ArgumentComment).filter(ArgumentComment.argument_id.in_(session['argument_ids'])).order_by(ArgumentComment.argument_id, ArgumentComment.created_datetime.desc()).all()
    comment_ids = [user[0].id for user in comments_query]
    all_arguments = []
    for arg in arguments:
        all_arguments.append([arg,[com for com in comments_query if com[1].argument_id == arg.id]])
    session['motion_ids'] = [argument.motion_id for argument in arguments]
    user_status = session['user_status']
    topics = db.session.query(func.count(Topic.id)).filter_by(status = True).all()[0][0]
    randnum = random.choice(range(1, topics + 1))
       
    return render_template("vote_argument.html", user_status=user_status, all_arguments=all_arguments, topic=topic, other_user_motions=other_user_motions, randnum=randnum, user_points=user_points)

@app.route('/scoring2', methods=['GET'])
@login_required
def scoring2():
    user_points = get_user_points()
    category_filter = request.args.get('category_value', 'all')
    categories = db.session.query(Topic.category).distinct()
    user_motions = Motion.query.filter_by(user_id = session['user_id']).all()
    user_topics = [motion.topic_id for motion in user_motions]
    motions = db.session.query(Topic).filter(Topic.id.in_(user_topics))
    print request.form.getlist('choice')
    return render_template("scoring2.html", user_points=user_points, categories=categories, motions=motions)    
  
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
    
def get_user_points():
    user = User.query.filter_by(id=session['user_id'])
    return int(user[0].points)

def update_topic_status():
    active_topics = db.session.query(Topic).filter_by(status = True).all()
    for topic in active_topics:
        if "Closed" in topic.days_left():
            updated_topic = Topic.query.get(topic.id)
            updated_topic.status = False
            db.session.commit()
 
if __name__ == '__main__':
    app.run(debug=True)
