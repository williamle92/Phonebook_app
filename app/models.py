from operator import index
from app import db, login
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_login import UserMixin

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(150),nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password=generate_password_hash(password)
    

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User: {self.username}>'



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150),nullable=False)
    address = db.Column(db.String(100))
    phonenumber = db.Column(db.String(15), nullable=False)
    workphonenumber = db.Column(db.String(15))
    homephonenumber = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, firstname, lastname, email, address, phonenumber, workphonenumber, homephonenumber, user_id):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.address = address
        self.phonenumber = phonenumber
        self.workphonenumber = workphonenumber
        self.homephonenumber = homephonenumber
        self.user_id = user_id

    def __repr__(self):
        return '<Contact {}>'.format(self.firstname)


