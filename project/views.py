from flask import render_template, redirect, url_for, request, session, flash, g, send_from_directory, jsonify
from functools import wraps
from forms import LoginForm, RegisterForm, ArgumentsForm, VoteArgumentsForm, ProposedTopicForm
from sqlalchemy.sql import func
import random
from models import *
import datetime
from operator import itemgetter
import datetime
from project.models import bcrypt
from project import app

@app.route('/')
def home():
    # Refresh topics
    update_topic_status()
    # Create list of all active motions by category
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
    # Not logged in --> Only give list of all active motions by category
    if 'logged_in' not in session:
        return render_template('about.html', all_motions = all_motions)
    # Get a random a topic number the user has submitted motions for
    user_topics = db.session.query(Topic.id).distinct().join(Motion).filter(Motion.user_id == session['user_id'])
    user_topics = [top[0] for top in user_topics]
    if user_topics == []:
        randnum = 1
    else:
        randnum = random.sample(user_topics, 1)[0]
    # Get users current points
    user_points = get_user_points()
    # Get a random proposed motion 
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
    
@app.route('/propose-motion', methods=['GET', 'POST'])
@login_required
def add_proposed_topic():
    # Get users current points
    points = get_user_points()
    # Not enough points to propose a motion
    if points < 30:
        flash("You don't have enough points to propose your own debate motions! You need to earn more by voting on arguments.")
        return redirect(url_for('home'))
    # Get count of all user votes by active topic to make sure they have voted >= 9 times on each active motion
    categories = db.session.query(Topic.category).distinct()
    closed_topics = db.session.query(Topic.id).filter_by(status = False).all()
    closed_topics = [elem[0] for elem in closed_topics]
    votes_per_topic = db.session.query(Motion.topic_id, func.count(Vote.id)).join(Vote).filter(~ Motion.topic_id.in_(closed_topics), Vote.voter_id == session['user_id']).group_by(Motion.topic_id).all()
    for tuple in votes_per_topic:
        if tuple[1] < 9:
            message = "You need to vote on arguments at least 9 times for every new debate you enter before proposing your own. You need to vote {integer} more times on this issue.".format(integer = 9 - tuple[1])
            url = "/voting/{interger}".format(interger = tuple[0])
            flash(message)
            return redirect(url)      
    form = ProposedTopicForm()
    if form.validate_on_submit():
        # Add proposed topic and subtract 30 points from user's current balance
        proposed_topic = ProposedTopic(request.form['category_value'], form.proposed_topic.data, session['user_id'])
        db.session.add(proposed_topic)
        user = User.query.filter_by(id=session['user_id'])
        user[0].points -= 30
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_topic.html', categories=categories, points=points, form=form)
    
@app.route('/edit-motion/<int:topic_number>', methods=['GET'])
@login_required
def get_edited_proposed_topic(topic_number):
    # Get all distinct categories and user's proposed topic
    categories = db.session.query(Topic.category).distinct()
    motion_update = ProposedTopic.query.get(topic_number)  
    return render_template('edit_topic.html', motion_update=motion_update, categories=categories)
    
    
@app.route('/edit-motion/<int:topic_number>', methods=['POST'])
@login_required
def add_edited_proposed_topic(topic_number):
    # Update proposed motion to reflect new edit
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
    # Bad topic number
    if proposed_topic == None:
        flash('The proposed motion you\'re trying to vote for doesn\'t exist.')
        return redirect(url_for('home'))
    # Did user propose the topic? 
    if proposed_topic.author_id == session['user_id']:
        user_proposed = True
    else:
        user_proposed = False
    # Get user's vote and comments on the proposed topic 
    current_user_query = db.session.query(ProposedTopicVote).filter_by(proposedtopic_id = topic_number)
    current_user = [vote.vote_value for vote in current_user_query if vote.author_id == session['user_id']]
    user_comment = db.session.query(ProposedTopicComment).filter_by(proposedtopic_id = topic_number, author_id = session['user_id'])
    user_comment = [com.comment for com in user_comment]
    # Get total number of up-votes and down-votes on proposed topic
    up_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = True, proposedtopic_id = topic_number)
    up_votes = up_votes[0][0]
    down_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = False, proposedtopic_id = topic_number)
    down_votes = down_votes[0][0]
    # Calculate up-vote share
    total_users = db.session.query(func.count(User.id))
    total_users = total_users[0][0]
    up_vote_share = round(float(up_votes) / float(total_users), 2)
    # Votes needed is tiered by how many total users there are
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
    # Get all comments for proposed topic
    comments_query = db.session.query(User, ProposedTopicComment).join(ProposedTopicComment).filter_by(proposedtopic_id = topic_number).order_by(ProposedTopicComment.created_datetime.desc()).all()
    # Get list of all other proposed topics by category
    other_propTopics = ProposedTopic.query.filter(ProposedTopic.id != topic_number).all()
    other_propCategories = db.session.query(ProposedTopic.category).distinct()
    user_available_propTopics = [{} for x in xrange(len(list(other_propCategories)))]
    for index, cat in enumerate(other_propCategories):
        temp_list = []
        for top in other_propTopics:
            if str(cat[0]) == str(top.category):
                temp_list.append(top)
                user_voted = db.session.query(ProposedTopicVote.id).filter_by(proposedtopic_id = top.id, author_id = session['user_id']).all()
                # if user_voted == []:
                    # temp_list.append("**You haven\'t voted on this**")
            else:
                pass
        user_available_propTopics[index][str(cat[0])] = temp_list     
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
    # Didn't submit a vote --> redirect back
    if vote_value == None:
        flash("You need to vote for or against the proposed motion.. ")
        return redirect(url)
    vote_update = db.session.query(ProposedTopicVote).filter_by(proposedtopic_id = topic_number, author_id=session['user_id']).all()
    new_vote = True if vote_value == 'true' else False
    # If no previous vote then add new one
    if vote_update == []:
        db.session.add(ProposedTopicVote(new_vote, topic_number, session['user_id']))
        db.session.commit()
    # Otherwise update vote
    else:
        vote_update[0].vote_value = new_vote
        db.session.commit()
    # Get user comment on proposed vote 
    # Update with new comment if there was one previously
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
    
    # Get total up-votes, users, up_vote share
    up_votes = db.session.query(func.count(ProposedTopicVote.id)).filter_by(vote_value = True, proposedtopic_id = topic_number)
    up_votes = up_votes[0][0]
    total_users = db.session.query(func.count(User.id))
    total_users = total_users[0][0]
    up_vote_share = round(float(up_votes) / float(total_users), 2)
    
    activated_motion_url = "/arguments"
    
    # Criteria for when proposed motion passes depends on total up-votes relative to total users
    if total_users <= 5:
        if up_votes >= 3:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is now active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 5 and total_users <= 10:
        if up_votes >= 4:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is now active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 10 and total_users <= 25:
        if up_votes >= 5:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is now active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 25 and total_users <= 100:
        if vote_share > 0.15:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is now active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 100 and total_users <= 500:
        if vote_share > 0.10:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is now active for debate. Add your arguments!')
            return redirect(activated_motion_url)
    elif total_users > 500:
        if vote_share > 0.05:
            activate_proposed_motion(topic_number)
            flash('The proposed motion you just voted on has successfully passed and is now active for debate. Add your arguments!')
            return redirect(activated_motion_url)            
    else:
        pass
    
    db.session.commit()
    return redirect(url) 

def activate_proposed_motion(integer):
    # Activates proposed motion
    proposed_motion = ProposedTopic.query.get(integer)
    db.session.add(Topic(proposed_motion.category, proposed_motion.topic, proposed_motion.author_id, True))
    db.session.delete(proposed_motion)
    db.session.commit()    

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Registration requires username, e-mail, and password
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        session['logged_in'] = True
        session['user_id'] = user.id
        flash('Thanks for registering!')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/arguments', methods=['POST','GET'])
@login_required
def add_arguments():
    # Get user's current points total
    user_points = get_user_points()
    # Update to close topics (motions) that should no longer be active
    update_topic_status()
    # Get all topic categories and motions ids the user has submitted
    category_filter = request.args.get('category_value', 'all')
    categories = db.session.query(Topic.category).distinct()
    user_motions = Motion.query.filter_by(user_id = session['user_id']).all()
    user_topics = [motion.topic_id for motion in user_motions]
    print user_topics
    # Allow users to filter to topics --which they haven't submitted arguments for-- by category
    if category_filter == 'all':
        motions = db.session.query(Topic).filter(~ Topic.id.in_(user_topics), Topic.status == True)
        category_header = "All"
    else:
        motions = db.session.query(Topic).filter(~ Topic.id.in_(user_topics), Topic.category == category_filter, Topic.status == True)
        category_header = category_filter
    # Get a random topic the user has submitted arguments for
    # Can send them to vote more or see the highest rated turing arguments for this random topic
    topics = db.session.query(func.count(Topic.id)).filter_by(status = True).all()[0][0]
    active_user_topics = db.session.query(Topic.id).filter(Topic.id.in_(user_topics), Topic.status == True)
    active_user_topic_ids = [id[0] for id in active_user_topics]
    randnum = random.choice(active_user_topic_ids)
    
    # POST request
    # form handling for arguments user tries to submit
    form = ArgumentsForm()
    if form.validate_on_submit():
        # Get total votes user has casted for each motion they are active in. 
        # User needs to vote on at least 9 other arguments for every debate they join before they can submit arguments to join a new debate.
        votes_per_topic = db.session.query(Motion.topic_id, func.count(Vote.id)).join(Vote).filter(Motion.topic_id.in_(user_topics), Vote.voter_id == session['user_id']).group_by(Motion.topic_id).all()
        print votes_per_topic
        for position, tuple in enumerate(votes_per_topic):
            print tuple[0], position
            if tuple[0] != user_topics[position]:
                # if casted less than 9 votes send back to finish voting on user's active topic 
                message = "You need to vote on arguments at least 9 times for every new debate you enter before proposing your own. You need to vote 9 more times on this issue."
                url = "/voting/{integer}".format(integer = user_topics[position])
                flash(message)
                return redirect(url)
            if tuple[1] < 9:
                message = "You need to vote on arguments at least 9 times for every new debate you enter before proposing your own. You need to vote {integer} more times on this issue.".format(integer = 9 - tuple[1])
                url = "/voting/{integer}".format(integer = tuple[0])
                flash(message)
                return redirect(url)
        topic_id = db.session.query(Topic).filter_by(topic = request.form['motion_value'], status = True).all()[0]
        if request.form['user_stance'] == "pro":
            added_motion = Motion(topic_id.id, session['user_id'], True)
            db.session.add(added_motion)
        else:
            added_motion = Motion(topic_id.id, session['user_id'], False)
            db.session.add(added_motion)
        motion_id = db.session.query(Motion.id).order_by(Motion.id.desc()).first()[0]
        pro_argument = Argument(True, form.pro_abstract.data, form.pro_argument.data, session['user_id'], motion_id)
        con_argument = Argument(False, form.con_abstract.data, form.con_argument.data, session['user_id'], motion_id)
        db.session.add(pro_argument)
        db.session.add(con_argument)

        user = User.query.filter_by(id=session['user_id'])
        user[0].points -= 15
        db.session.commit()
        
        flash("You just submitted your arguments which other users will vote on. Now go vote on theirs and earn some credits back!")
        url = "/voting/{integer}".format(integer = topic_id.id)
        return redirect(url)       
    return render_template('arguments.html', form=form, category_header = category_header, categories=categories, motions=motions, randnum=randnum, user_points=user_points)

    
@app.route('/voting/<int:topic_number>', methods=['GET','POST'])
@login_required    
def voting(topic_number):
    user = User.query.filter_by(id=session['user_id'])
    form = VoteArgumentsForm()
    user_motion = db.session.query(Motion).filter_by(topic_id = topic_number, user_id = session['user_id']).all()
    if form.validate_on_submit():
        user_turing_pos = not user_motion[0].user_procon
        user_turing_arg = db.session.query(Argument).filter_by(motion_id = user_motion[0].id, procon = user_turing_pos).all()
        user_turing_votes = db.session.query(func.count(Vote.id)).filter_by(argument_id = user_turing_arg[0].id).all()[0][0]
        # For production version adjust this 15 number (minimal number of argument votes) to optimal setting
        if user_turing_votes > 15:
            user_turing_avg = round(db.session.query(func.avg(Vote.value)).filter_by(argument_id = user_turing_arg[0].id).all()[0][0], 2)
            opp_motion_ids = db.session.query(Motion.id).filter_by(topic_id = topic_number, user_procon = user_turing_pos).all()
            opp_motion_ids = [motion[0] for motion in opp_motion_ids]
            opp_turing_args = db.session.query(Argument.id).filter(Argument.motion_id.in_(opp_motion_ids), Argument.procon == user_motion[0].user_procon).all()
            opp_turing_args = [arg[0] for arg in opp_turing_args]
            opp_turing_votes = db.session.query(Vote.argument_id, func.count(Vote.id)).filter(Vote.argument_id.in_(opp_turing_args)).group_by(Vote.argument_id).all()
            valid_opp_tur_ids = [tur_arg[0] for tur_arg in opp_turing_votes if tur_arg[1] > 15]
            valid_opp_tur_score = round(db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(valid_opp_tur_ids)).all()[0][0], 1)
            extra_votes = user_turing_avg - valid_opp_tur_score
            extra_votes = int(extra_votes)
            if 1 < extra_votes <= 4:
                for integer in range(0, extra_votes):
                    db.session.add(Vote(session['argument_ids'][0], session['motion_ids'][0], form.first_vote.data, session['user_id']))
                    db.session.add(Vote(session['argument_ids'][1], session['motion_ids'][1], form.second_vote.data, session['user_id']))
                    db.session.add(Vote(session['argument_ids'][2], session['motion_ids'][2], form.third_vote.data, session['user_id']))
                message = "The high turing score on your own argument for this motion gets you an additional {integer} duplicate votes!".format(integer = extra_votes - 1)
                flash(message)
            else:
                db.session.add(Vote(session['argument_ids'][0], session['motion_ids'][0], form.first_vote.data, session['user_id']))
                db.session.add(Vote(session['argument_ids'][1], session['motion_ids'][1], form.second_vote.data, session['user_id']))
                db.session.add(Vote(session['argument_ids'][2], session['motion_ids'][2], form.third_vote.data, session['user_id']))
        else:           
            db.session.add(Vote(session['argument_ids'][0], session['motion_ids'][0], form.first_vote.data, session['user_id']))
            db.session.add(Vote(session['argument_ids'][1], session['motion_ids'][1], form.second_vote.data, session['user_id']))
            db.session.add(Vote(session['argument_ids'][2], session['motion_ids'][2], form.third_vote.data, session['user_id']))
        for number in range(0, 3):
            comment_field = request.form.get('comment' + str(session['argument_ids'][number]), None)
            if comment_field == None or comment_field == "":
                pass
            else:
                user_comment = db.session.query(ArgumentComment).filter_by(argument_id = session['argument_ids'][number], author_id = session['user_id']).all()
                if user_comment == []:
                    db.session.add(ArgumentComment(comment_field, session['argument_ids'][number], session['user_id']))
                    print "submitting comment " + comment_field + " for argument id " + str(session['argument_ids'][number])
                else:
                    user_comment[0].comment = comment_field
                    user_comment[0].created_datetime = datetime.datetime.now()
        user[0].points += 3
        db.session.commit()
        url = "/voting/{integer}".format(integer = topic_number)
        return redirect(url)
    if user_motion == []:
        flash('You need to submit arguments for that motion before you can vote!')
        return redirect(url_for('add_arguments'))
    update_topic_status()
    other_topics = Topic.query.join(Motion, User).filter(Motion.topic_id != topic_number, User.id == session['user_id'], Topic.status == True).all()
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
    user_points = get_user_points()
    if user_motion[0].user_procon == True:
        session['user_status'] = True
        displayable_arguments = Argument.query.join(Motion, Topic).filter(Argument.procon == True, Topic.id == topic_number, Topic.status == True).all()
        print displayable_arguments
    else:
        session['user_status'] = False
        displayable_arguments = Argument.query.join(Motion, Topic).filter(Argument.procon == False, Topic.id == topic_number, Topic.status == True).all()
    displayable_arguments = [arg for arg in displayable_arguments if arg.author_id != session['user_id']]
    arguments = displayable_arguments
    try:
        arguments = random.sample(displayable_arguments, 3)
    except ValueError:
        # not enough arguments submitted to vote on (3 minimum)
        flash("There\'s not enough arguments to vote on for this motion. Check back soon!")
        return redirect(url_for('home'))
    if request.method == 'POST' and form.validate_on_submit() is False:
        # Form error
        # Keep the same arguments (arg IDs stored in session) until user puts in valid input
        first_orig_arg = Argument.query.filter(Argument.id == session['argument_ids'][0])[0]
        second_orig_arg = Argument.query.filter(Argument.id == session['argument_ids'][1])[0]
        third_orig_arg = Argument.query.filter(Argument.id == session['argument_ids'][2])[0]
        arguments = [first_orig_arg, second_orig_arg, third_orig_arg]        
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
    return render_template("vote_argument.html", form=form, user_status=user_status, all_arguments=all_arguments, topic=topic, other_user_motions=other_user_motions, randnum=randnum, user_points=user_points)     


@app.route('/turingarguments/topic/<int:topic_id>/topscoring', methods=['GET'])
@login_required
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
    # return render_template('login.html', form=form)
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

@app.route('/scoring', methods=['GET'])
@login_required            
def scoring():
    user_motions = Motion.query.filter_by(user_id = session['user_id']).all()
    user_topic_ids = [motion.topic_id for motion in user_motions] 
    
    categories = db.session.query(Topic.category).distinct().filter(Topic.id.in_(user_topic_ids)).all()
    filtered_categories = [str(request.args.get(i[0])) for i in categories if request.args.get(i[0]) != None]
    
    if len(categories) != len(filtered_categories) and len(filtered_categories) > 0:
        topic_ids = db.session.query(Topic.id).filter(Topic.category.in_(filtered_categories)).all()
        topic_ids = [i[0] for i in topic_ids]
        user_motions = [motion for motion in user_motions if motion.topic_id in topic_ids]
        
    if request.args.get('open_filter') is not None and request.args.get('closed_filter') == None:
        topic_ids = db.session.query(Topic.id).filter(Topic.status == True).all()
        topic_ids = [i[0] for i in topic_ids]
        user_motions = [motion for motion in user_motions if motion.topic_id in topic_ids]

    if request.args.get('open_filter') == None and request.args.get('closed_filter') is not None:
        topic_ids = db.session.query(Topic.id).filter(Topic.status == False).all()
        topic_ids = [i[0] for i in topic_ids]        
        user_motions = [motion for motion in user_motions if motion.topic_id in topic_ids]
   
    motions = []
    opponent_turing_args_ids = []
    opponent_true_args_ids = []
    user_turing_args_ids = []
    user_true_args_ids = []
    for motion in user_motions:
        arguments = db.session.query(Argument).filter(Argument.motion_id == motion.id).all()
        topic = db.session.query(Topic).filter(Topic.id == motion.topic_id)
        numbers = []
        opp_user_boolean = not motion.user_procon
        opponent_motions = db.session.query(Motion.id).filter(Motion.topic_id == motion.topic_id, Motion.user_procon == opp_user_boolean).all()
        opponent_motions = [mot[0] for mot in opponent_motions]
        opponent_arg_ids = db.session.query(Argument).filter(Argument.motion_id.in_(opponent_motions)).all()
        user_turing_arg_ind = True
        for arg in arguments:
            if motion.user_procon == arg.procon:
                user_turing_arg_ind = False
                user_true_args_ids.append(arg.id)
                for opp_arg in opponent_arg_ids:
                    if opp_arg.procon == arg.procon:
                        opponent_turing_args_ids.append(opp_arg.id)
                    else:
                        opponent_true_args_ids.append(opp_arg.id)
            else:
                user_turing_args_ids.append(arg.id)
            arg_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id == arg.id)[0][0]
            arg_score = round(db.session.query(func.avg(Vote.value)).filter(Vote.argument_id == arg.id).all()[0][0], 2) if arg_votes > 0 else 0
            motion_ids = db.session.query(Motion.id).filter(Motion.topic_id == topic[0].id, Motion.user_procon != motion.user_procon).all()
            motion_ids = [mot[0] for mot in motion_ids]
            argument_ids = db.session.query(Argument.id).filter(Argument.motion_id.in_(motion_ids), Argument.procon == arg.procon).all()
            argument_ids = [arg[0] for arg in argument_ids]
            opp_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id.in_(argument_ids))[0][0]
            opp_avg_score = round(db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(argument_ids)).all()[0][0], 2) if opp_votes > 0 else 0
            numbers.append(opp_votes)
            numbers.append(opp_avg_score)
            numbers.append(arg_votes)
            numbers.append(arg_score)  
        motions.append([topic, arguments, numbers, motion.user_procon])
    user_turing_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id.in_(user_turing_args_ids))[0][0]
    user_turing_avg = db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(user_turing_args_ids))
    user_turing_avg = round(user_turing_avg[0][0], 2)
    user_true_votes = db.session.query(func.count(Vote.id)).filter(Vote.argument_id.in_(user_true_args_ids))[0][0]
    user_true_avg = db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(user_true_args_ids))
    user_true_avg = round(user_true_avg[0][0], 2)
    opp_true_arg_votes = db.session.query(Argument.author_id, func.avg(Vote.value)).join(Vote).filter(Argument.id.in_(opponent_true_args_ids)).group_by(Argument.author_id).all()
    opp_true_avg = round(db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(opponent_true_args_ids))[0][0], 2)
    user_turing_percentile = round(((float(len([round(avg[1], 2) for avg in opp_true_arg_votes if round(avg[1], 2) < user_turing_avg])) / len(opp_true_arg_votes))*100), 1)
    opp_turing_arg_votes = db.session.query(Argument.author_id, func.avg(Vote.value)).join(Vote).filter(Argument.id.in_(opponent_turing_args_ids)).group_by(Argument.author_id).all()
    opp_turing_avg = round(db.session.query(func.avg(Vote.value)).filter(Vote.argument_id.in_(opponent_turing_args_ids))[0][0], 2)
    user_true_percentile = round(((float(len([round(avg[1], 2) for avg in opp_turing_arg_votes if round(avg[1], 2) < user_true_avg])) / len(opp_turing_arg_votes))*100), 1)
    summary_statistics = [user_turing_votes, user_turing_avg, opp_true_avg, user_turing_percentile, user_true_votes, user_true_avg, opp_turing_avg, user_true_percentile]
    user_points = get_user_points()
    return render_template('scoring.html', motions = motions, categories = categories, summary_statistics = summary_statistics, user_points = user_points)