from flask import Flask, flash, redirect, url_for
import os
from dotenv import load_dotenv
from .user import login_manager
from flask_login import login_required, current_user
from .routes import main 
from .user import login_bp as auth
from .database_utils import init_db

def create_app():
    load_dotenv()
    app=Flask(__name__, instance_relative_config=False)
    app.config["UPLOAD_FOLDER"]="app/static/uploads"
    app.config["MAX_CONTENT_LENGTH"]=50*1024*1024
    app.secret_key=os.getenv("SECRET_KEY")
    
   
    #initialize DB+MIGRATION
    init_db(app)
    login_manager.init_app(app)
    #IMPORT ROUTES SO THAT FLASK KNOWS ABOUT THEM

    app.register_blueprint(main,url_prefix="/")
    app.register_blueprint(auth,url_prefix="/auth")

    return app