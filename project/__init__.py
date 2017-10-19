from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt



app = Flask(__name__)
app.config.from_object('config.BaseConfig')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from views import *