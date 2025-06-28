from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin

db = SQLAlchemy()
migrate=Migrate()

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True, nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password_hash=db.Column(db.String(128), nullable=False)
    
    entries=db.relationship("Entry",back_populates="user",lazy="dynamic")
    
class Entry(db.Model):
    __tablename__="entries"
    id=db.Column(db.Integer,primary_key=True)
    timestamp=db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    entry_type=db.Column(db.String(10),nullable=False)
    content=db.Column(db.Text, nullable=False)
    summary=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"),nullable=True)
    
    user=db.relationship("User",back_populates="entries")
    
def init_db(app):
    #you can override URI via environment or config
    app.config.setdefault("SQLALCHEMY_DATABASE_URI","sqlite:///knowspace.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS",False)
    db.init_app(app)
    migrate.init_app(app,db)
    
    
