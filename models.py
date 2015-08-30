from app import db, bcrypt

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class ArgumentPost(db.Model):

    __tablename__ = "arguments"

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String, nullable=False)
    procon_topic = db.Column(db.Boolean, nullable=False)
    user_procon = db.Column(db.Boolean, nullable=False)
    abstract = db.Column(db.String, nullable=False)
    argument = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, topic, procon_topic, user_procon, abstract, argument, author_id):
        self.topic = topic
        self.procon_topic = procon_topic
        self.user_procon = user_procon
        self.abstract = abstract
        self.argument = argument
        self.author_id = author_id

    def __repr__(self):
        return '<abstract {}'.format(self.abstract)
        
        
class User(db.Model):

    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    posts = relationship("ArgumentPost", backref="author")
    
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
    value = db.Column(db.Integer, nullable=False)
    voter_id =  db.Column(db.Integer, ForeignKey('users.id'))
    
    def __init__(self, argument_id, value, voter_id):
        self.argument_id = argument_id
        self.value = value
        self.voter_id = voter_id
        
        
    def __repr__(self):
        return '<name {}'.format(self.value)
    
    