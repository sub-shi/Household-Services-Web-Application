from dotenv import load_dotenv 
import os
from os import getenv 
from app import app
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRICK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRICK_MODIFICATIONS')
app.config['SECRET_KEY']= os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'static/uploads/'      # STORING IN STATIC/UPLOADS FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

