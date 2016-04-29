from app import db, bcrypt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime

class ProposedTopic(db.Model):

    __tablename__ = "proposed_topics"
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    topic = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    created_date = db.Column(db.Date, default=datetime.date.today)
    
    def __init__(self, category, topic, author_id):
        self.category = category
        self.topic = topic
        self.author_id = author_id
        
    # Update interger below to actual time allowance
    def days_left(self):
        days_remaining = 20 - (datetime.date.today() - self.created_date).days
        if days_remaining > 1:
            return "{int} days remaining".format(int = days_remaining)
        elif days_remaining == 1: 
            return "*1 day remaining*"
        else:
            return "Closed."
        
    def __repr__(self):
        return self.topic
        
class ProposedTopicVote(db.Model):

    __tablename__ = "proposed_votes"
    
    id = db.Column(db.Integer, primary_key=True)
    vote_value = db.Column(db.Boolean, nullable=False)
    # True = up-vote, False = down-vote
    proposedtopic_id = db.Column(db.Integer, ForeignKey('proposed_topics.id'))
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    
    def __init__(self, vote_value, proposedtopic_id, author_id):
        self.vote_value = vote_value
        self.proposedtopic_id = proposedtopic_id
        self.author_id = author_id
        
    # def __repr__(self):
        # return self.author_id
        
class ProposedTopicComment(db.Model):

    __tablename__ = "proposed_comments"
    
    id = db.Column(db.Integer, primary_key=True)
    created_datetime = db.Column(db.DateTime, default=datetime.datetime.now())
    comment = db.Column(db.String, nullable=False)
    proposedtopic_id = db.Column(db.Integer, ForeignKey('proposed_topics.id'))
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    
    def __init__(self, comment, proposedtopic_id, author_id):
        self.comment = comment
        self.proposedtopic_id = proposedtopic_id
        self.author_id = author_id
        
    def time_since(self):
        time_since = datetime.datetime.now() - self.created_datetime
        seconds_since = int(time_since.total_seconds())
        minutes_since = int(time_since.total_seconds() / 60)
        hours_since = int(minutes_since / 60)
        days_since = time_since.days
        weeks_since = int(days_since / 7)
        months_since = int(days_since / 30)
        years_since = int(months_since / 12)
        # return True if sum([a, b]) % 10 == 0 else False
        if seconds_since < 60: 
            #if seconds_since == 1: return "{time} SECOND AGO".format(time = seconds_since) else return "{time} SECONDS AGO".format(time = seconds_since)
            if seconds_since == 1: return "{time} SECOND AGO".format(time = seconds_since)
            return "{time} SECONDS AGO".format(time = seconds_since)
        if minutes_since < 60:
            if minutes_since == 1: return "{time} MINUTE AGO".format(time = minutes_since)
            return "{time} MINUTES AGO".format(time = minutes_since)
        if hours_since < 24:
            if hours_since == 1: return "{time} HOUR AGO".format(time = hours_since)
            return "{time} HOURS AGO".format(time = hours_since)
        if days_since < 7:
            if days_since == 1: return "{time} DAY AGO".format(time = days_since)
            return "{time} DAYS AGO".format(time = days_since)
        if weeks_since < 7:
            if weeks_since == 1: return "{time} WEEK AGO".format(time = weeks_since)
            return "{time} WEEKS AGO".format(time = weeks_since)
        if months_since < 12:
            if months_since == 1: return "{time} MONTH AGO".format(time = months_since)
            return "{time} MONTHS AGO".format(time = months_since)
        if years_since == 1: return "{time} YEAR AGO".format(time = years_since)
        return "{time} YEARS AGO".format(time = years_since)            
        
    def __repr__(self):
        return self.comment

class Topic(db.Model):

    __tablename__ = "topics"
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    topic = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    created_date = db.Column(db.Date, default=datetime.date.today)
    # True = Active, False = closed
    status = db.Column(db.Boolean, nullable=False)
    
    def __init__(self, category, topic, author_id, status):
        self.category = category
        self.topic = topic
        self.author_id = author_id
        self.status = status
        
    # Update interger below to actual time allowance
    # Remove 'and self.status == True'. Only necessary for development
    def days_left(self):
        days_remaining = 100 - (datetime.date.today() - self.created_date).days
        if days_remaining > 1 and self.status == True:
            return "{int} days remaining".format(int = days_remaining)
        elif days_remaining == 1 and self.status == True: 
            return "*1 day remaining*"
        else:
            # Adjust close_date below to non-development correct version
            return "Closed on {close_date}".format(close_date = self.created_date - datetime.timedelta(days = 10))
        
    def __repr__(self):
        return self.topic
        

class Motion(db.Model):

    __tablename__ = "motions"
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, ForeignKey('topics.id'))
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    user_procon = db.Column(db.Boolean, nullable=False)
    
    def __init__(self, topic_id, user_id, user_procon):
        self.topic_id = topic_id
        self.user_id = user_id
        self.user_procon = user_procon
        
    def __repr__(self):
        return '<abstract {}'.format(self.user_procon)


class Argument(db.Model):

    __tablename__ = "arguments"

    id = db.Column(db.Integer, primary_key=True)
    procon = db.Column(db.Boolean, nullable=False)
    abstract = db.Column(db.String, nullable=False)
    argument = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    motion_id = db.Column(db.Integer, ForeignKey('motions.id'))

    def __init__(self, procon, abstract, argument, author_id, motion_id):
        self.procon = procon
        self.abstract = abstract
        self.argument = argument
        self.author_id = author_id
        self.motion_id = motion_id

    def __repr__(self):
        return '<abstract {}'.format(self.abstract)

        
class ArgumentComment(db.Model):

    __tablename__ = "argument_comments"
    
    id = db.Column(db.Integer, primary_key=True)
    created_datetime = db.Column(db.DateTime, default=datetime.datetime.now())
    comment = db.Column(db.String, nullable=False)
    argument_id = db.Column(db.Integer, ForeignKey('arguments.id'))
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    
    def __init__(self, comment, argument_id, author_id):
        self.comment = comment
        self.argument_id = argument_id
        self.author_id = author_id
        
    def time_since(self):
        time_since = datetime.datetime.now() - self.created_datetime
        seconds_since = int(time_since.total_seconds())
        minutes_since = int(time_since.total_seconds() / 60)
        hours_since = int(minutes_since / 60)
        days_since = time_since.days
        weeks_since = int(days_since / 7)
        months_since = int(days_since / 30)
        years_since = int(months_since / 12)
        # return True if sum([a, b]) % 10 == 0 else False
        if seconds_since < 60: 
            #if seconds_since == 1: return "{time} SECOND AGO".format(time = seconds_since) else return "{time} SECONDS AGO".format(time = seconds_since)
            if seconds_since == 1: return "{time} SECOND AGO".format(time = seconds_since)
            return "{time} SECONDS AGO".format(time = seconds_since)
        if minutes_since < 60:
            if minutes_since == 1: return "{time} MINUTE AGO".format(time = minutes_since)
            return "{time} MINUTES AGO".format(time = minutes_since)
        if hours_since < 24:
            if hours_since == 1: return "{time} HOUR AGO".format(time = hours_since)
            return "{time} HOURS AGO".format(time = hours_since)
        if days_since < 7:
            if days_since == 1: return "{time} DAY AGO".format(time = days_since)
            return "{time} DAYS AGO".format(time = days_since)
        if weeks_since < 7:
            if weeks_since == 1: return "{time} WEEK AGO".format(time = weeks_since)
            return "{time} WEEKS AGO".format(time = weeks_since)
        if months_since < 12:
            if months_since == 1: return "{time} MONTH AGO".format(time = months_since)
            return "{time} MONTHS AGO".format(time = months_since)
        if years_since == 1: return "{time} YEAR AGO".format(time = years_since)
        return "{time} YEARS AGO".format(time = years_since)            
        
    def __repr__(self):
        return self.comment
    
        
class User(db.Model):

    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        
    def __repr__(self):
        return '<name {}'.format(self.name)
        
        
class Vote(db.Model):

    __tablename__ = "votes"
    
    id = db.Column(db.Integer, primary_key=True)
    argument_id = db.Column(db.Integer, ForeignKey('arguments.id'))
    motion_id = db.Column(db.Integer, ForeignKey('motions.id'))
    value = db.Column(db.Integer, nullable=False)
    voter_id =  db.Column(db.Integer, ForeignKey('users.id'))
    
    def __init__(self, argument_id, motion_id, value, voter_id):
        self.argument_id = argument_id
        self.motion_id = motion_id
        self.value = value
        self.voter_id = voter_id
               
    def __repr__(self):
        return '<name {}'.format(self.value)

