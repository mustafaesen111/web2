from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

from ib_insync import IB

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "mysecret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)

# Login manager loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- IBKR Bağlantısı ve Veri Çekme Fonksiyonları ---
def fetch_ibkr_portfolio():
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=1)  # IB Gateway ya da TWS ayarlarına göre port ve clientId değişebilir
        portfolio = ib.portfolio()
        ib.disconnect()
        return portfolio
    except Exception as e:
        print(f"IBKR bağlantı hatası: {e}")
        return []

def fetch_ibkr_trades():
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=1)
        trades = ib.trades()
        ib.disconnect()
        return trades
    except Exception as e:
        print(f"IBKR bağlantı hatası: {e}")
        return []


# Routes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/portfolio')
@login_required
def portfolio():
    if not current_user.is_subscribed:
        flash("Bu sayfa sadece aboneler içindir.", "warning")
        return redirect(url_for('subscribe'))

    portfolio_data = fetch_ibkr_portfolio()
    # portfolio_data genelde ib_insync'in PortfolioItem objeleri listesi
    # Template'e uygun şekilde verilecek
    return render_template('portfolio.html', portfolio=portfolio_data)

@app.route('/trades')
@login_required
def trades():
    if not current_user.is_subscribed:
        flash("Bu sayfa sadece aboneler içindir.", "warning")
        return redirect(url_for('subscribe'))

    trades_data = fetch_ibkr_trades()
    # trades_data genelde ib_insync'in Trade objeleri listesi
    return render_template('trades.html', trades=trades_data)

@app.route('/performance')
@login_required
def performance():
    if not current_user.is_subscribed:
        flash("Bu sayfa sadece aboneler içindir.", "warning")
        return redirect(url_for('subscribe'))
    return render_template('performance.html')

@app.route('/copy_trade')
@login_required
def copy_trade():
    if not current_user.is_subscribed:
        flash("Bu sayfa sadece aboneler içindir.", "warning")
        return redirect(url_for('subscribe'))
    return render_template('copy_trade.html')

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

# Run locally
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


