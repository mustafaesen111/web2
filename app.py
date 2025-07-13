from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# IBKR API için
from ib_insync import IB

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "mysecret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Kullanıcı Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# IBKR veri çekme

def get_ibkr_portfolio():
    return [
        {'symbol': 'AAPL', 'quantity': 10, 'price': 190.00, 'value': 1900.00},
        {'symbol': 'MSFT', 'quantity': 5, 'price': 320.00, 'value': 1600.00},
    ]

def get_ibkr_trades():
    return [
        {'symbol': 'AAPL', 'quantity': 10, 'price': 185.00, 'action': 'BUY'},
        {'symbol': 'MSFT', 'quantity': 5, 'price': 310.00, 'action': 'BUY'},
    ]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash("Hatalı giriş bilgileri", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(email=email).first():
            flash("Bu email zaten kayıtlı", "warning")
            return redirect(url_for('signup'))
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Başarıyla kayıt olundu. Giriş yapabilirsiniz.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/gumroad-webhook', methods=['POST'])
def gumroad_webhook():
    payload = request.form
    email = payload.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_subscribed = True
            db.session.commit()
    return '', 200

@app.route('/portfolio')
@login_required
def portfolio():
    portfolio_data = get_ibkr_portfolio()
    return render_template('portfolio.html', portfolio=portfolio_data)

@app.route('/trades')
@login_required
def trades():
    trades_data = get_ibkr_trades()
    return render_template('history.html', trades=trades_data)

@app.route('/performance')
@login_required
def performance():
    return render_template('performance.html')

@app.route('/copy-trade')
@login_required
def copy_trade():
    return render_template('copy_trade.html')

# Geçici olarak veritabanı oluşturma route'u
@app.route('/init-db')
def init_db():
    db.create_all()
    return "Veritabanı oluşturuldu!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
