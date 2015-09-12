from app2 import db, bcrypt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime


class Topic(db.Model):

    __tablename__ = "topics"
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    topic = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, category, topic, author_id):
        self.category = category
        self.topic = topic
        self.author_id = author_id
        
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


class ProArgument(db.Model):

    __tablename__ = "pro_arguments"

    id = db.Column(db.Integer, primary_key=True)
    abstract = db.Column(db.String, nullable=False)
    argument = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    motion_id = db.Column(db.Integer, ForeignKey('motions.id'))

    def __init__(self, abstract, argument, author_id, motion_id):
        self.abstract = abstract
        self.argument = argument
        self.author_id = author_id
        self.motion_id = motion_id

    def __repr__(self):
        return '<abstract {}'.format(self.abstract)

        
class ConArgument(db.Model):

    __tablename__ = "con_arguments"

    id = db.Column(db.Integer, primary_key=True)
    abstract = db.Column(db.String, nullable=False)
    argument = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    motion_id = db.Column(db.Integer, ForeignKey('motions.id'))

    def __init__(self, abstract, argument, author_id, motion_id):
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
        
        
class ProVote(db.Model):

    __tablename__ = "pro_votes"
    
    id = db.Column(db.Integer, primary_key=True)
    argument_id = db.Column(db.Integer, ForeignKey('pro_arguments.id'))
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

        
class ConVote(db.Model):

    __tablename__ = "con_votes"
    
    id = db.Column(db.Integer, primary_key=True)
    argument_id = db.Column(db.Integer, ForeignKey('con_arguments.id'))
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