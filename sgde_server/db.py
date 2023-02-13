from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy

from .args import Args

db = SQLAlchemy()


@dataclass
class User(db.Model):
    username: str

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(Args.MAX_USERNAME_LENGTH), unique=True, nullable=False)
    password = db.Column(db.String(Args.MAX_PASSWORD_LENGTH), nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True)
    generators = db.relationship("Generator", backref="user", lazy=True)


@dataclass
class Task(db.Model):
    name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(Args.MAX_TASK_NAME_LENGTH), unique=True, nullable=False)
    directory = db.Column(db.String(36))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    generators = db.relationship("Generator", backref="task", lazy=True)


@dataclass
class Generator(db.Model):
    name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(Args.MAX_GENERATOR_NAME_LENGTH), nullable=False)
    filename = db.Column(db.String(Args.MAX_FILE_PATH_LENGTH), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
