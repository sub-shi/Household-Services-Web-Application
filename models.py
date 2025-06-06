
from flask import Flask, render_template, request, url_for, redirect, flash 
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from app import app 
db=SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
app.app_context().push()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

login_manager.login_view = "userlogin"

# for user database 
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, nullable = False)
    username = db.Column(db.String(32), unique = True, nullable = False)
    role = db.Column(db.String(50), nullable=False, default='admin')
    service_type = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String, nullable = True)
    password_hash=db.Column(db.String,nullable=False)
    is_admin = db.Column(db.Boolean, nullable = False, default = False)
    status = db.Column(db.String(20), nullable=False, default='active') 

    @property
    def password(self):
     return self.password

    @password.setter
    def password(self, plain_text_password):
     self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
     return bcrypt.check_password_hash(self.password_hash, attempted_password)
    

#for service professionals 
class service_professionals(db.Model):
    __tablename__ = 'service_professionals'
    id = db.Column(db.Integer, primary_key= True, autoincrement = True)
    name = db.Column(db.String, nullable = False)
    username = db.Column(db.String(32), unique = True, nullable = False)
    password_hash=db.Column(db.String,nullable=False)
    date_created = db.Column(db.Date, default=date.today()) 
    description = db.Column(db.String, nullable = True)
    service_type = db.Column(db.String, nullable = False) 
    experience = db.Column(db.Integer, nullable = False)
    profile_docs = db.Column(db.String, nullable = True) 
    role = db.Column(db.String(20), default='service_pro')
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False, default='active')


# for services data 
class services(db.Model):
      __tablename__ = 'services'
      id = db.Column(db.Integer, primary_key = True, autoincrement = True)
      name = db.Column(db.String, nullable = False)
      price = db.Column(db.Integer, nullable = False)
      time_required = db.Column(db.Integer, nullable=False)
      description = db.Column(db.String, nullable = True)
      pincode = db.Column(db.Integer, nullable = True)

#for service_requests data

class service_requests(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable = False, autoincrement = True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False, autoincrement = True) 
    professional_id  = db.Column(db.Integer, db.ForeignKey('service_professionals.id'), nullable = True, autoincrement = True)
    date_of_request = db.Column(db.Date, default = date.today())
    date_of_completion = db.Column (db.Date, nullable=True)
    service_status = db.Column(db.String, nullable = False, default='pending')
    remarks = db.Column(db.String, nullable = True)

    #Relationships
    service = db.relationship('services', backref='service_requests')
    customer = db.relationship('User', backref='service_requests')
    professional = db.relationship('service_professionals', backref='requests')



#cREATE DATABASE IF IT DOESN'T EXIST
with app.app_context():
   db.create_all()