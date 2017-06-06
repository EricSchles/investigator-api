from flask import Flask
from flask_script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from .commands import REPL
import os
from flask.ext.httpauth import HTTPBasicAuth

username,password = "eric_s","1234"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://"+username+":"+password+"@localhost/backpage_ads"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
#app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy dog"
db = SQLAlchemy(app)
migrate = Migrate(app,db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command("shell",REPL())
auth = HTTPBasicAuth()

from app import views,models
