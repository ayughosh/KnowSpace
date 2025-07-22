from flask import Blueprint, render_template,request,redirect,url_for,flash,current_app
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from .database_utils import User  # Adjust the import based on your project structure
from .database_utils import db    # Import db from your database_utils or the appropriate module

login_bp=Blueprint("auth",__name__)
login_manager=LoginManager()
login_manager.login_view="auth.login"

  # Use relative import if 'models.py' is in the same package

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="POST":
        username=request.form["username"].strip()
        email=request.form["email"].strip()
        password=request.form["password"].strip()
        if User.query.filter((User.username==username) | (User.email==email)).first():
            flash("Username or email already exists.", "warning")
        else:
            new=User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new);db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html")
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        email=request.form["email"].strip().lower()
        password=request.form["password"]
        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.home"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))