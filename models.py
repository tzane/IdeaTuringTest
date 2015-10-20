from app import db, bcrypt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime


class Topic(db.Model):

    __tablename__ = "topics"
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    topic = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    created_date = db.Column(db.Date, default=datetime.date.today)
    
    def __init__(self, category, topic, author_id):
        self.category = category
        self.topic = topic
        self.author_id = author_id
        
    # update interger below to actual time allowance
    def days_left(self):
        days_remaining = 100 - (datetime.date.today() - self.created_date).days
        if days_remaining > 1:
            return "{int} days remaining".format(int = days_remaining)
        elif days_remaining == 1: 
            return "*1 day remaining*"
        else:
            return "Closed."
        
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

