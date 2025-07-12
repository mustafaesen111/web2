from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
import os
import hmac
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mysecret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash("Login successful", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
        else:
            new_user = User(email=email, password=password, is_subscribed=False)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful. Please log in.", "success")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/portfolio')
@login_required
def portfolio():
    if not current_user.is_subscribed:
        flash("Please subscribe to access this page.", "warning")
        return redirect(url_for('subscribe'))
    return render_template('portfolio.html')

@app.route('/subscribe')
@login_required
def subscribe():
    return render_template('subscribe.html')

# ✅ GUMROAD WEBHOOK
@app.route('/gumroad-webhook', methods=['POST'])
def gumroad_webhook():
    try:
        secret = os.environ.get("GUMROAD_SECRET", "your_gumroad_secret")
        body = request.get_data()
        received_signature = request.headers.get("X-Gumroad-Signature", "")
        calculated_signature = hmac.new(
            secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, calculated_signature):
            return "Invalid signature", 403

        data = request.form
        email = data.get("email")

        user = User.query.filter_by(email=email).first()
        if user:
            user.is_subscribed = True
            db.session.commit()
            return "User updated", 200
        else:
            return "User not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)


