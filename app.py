from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# IBKR API
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

# Kullanıcı modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# IBKR portföy ve işlemler
def get_ibkr_portfolio():
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=1)
    portfolio = ib.portfolio()
    ib.disconnect()
    return portfolio

def get_ibkr_trades():
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=1)
    trades = ib.trades()
    ib.disconnect()
    return trades

# Ana sayfa
@app.route('/')
def home():
    return render_template('home.html')

# Abonelik sayfası
@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

# Kayıt
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Email ve şifre gereklidir.", "warning")
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash("Bu email zaten kayıtlı", "warning")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Kayıt başarılı, şimdi giriş yapabilirsiniz.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Giriş
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        try:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash("Giriş başarılı!", "success")
                return redirect(url_for('home'))
            else:
                flash("Email veya şifre hatalı.", "danger")
        except Exception as e:
            print(f"Giriş sırasında hata: {e}")
            flash("Sunucu hatası oluştu. Lütfen tekrar deneyin.", "danger")

    return render_template('login.html')

# Çıkış
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Çıkış yapıldı.", "info")
    return redirect(url_for('home'))

# GUMROAD webhook (abonelik)
@app.route('/gumroad-webhook', methods=['POST'])
def gumroad_webhook():
    email = request.form.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_subscribed = True
            db.session.commit()
    return '', 200

# Portföy sayfası (abonelik kontrolü geçici olarak KALDIRILDI!)
@app.route('/portfolio')
@login_required
def portfolio():
    try:
        portfolio_data = get_ibkr_portfolio()
    except Exception as e:
        print("Portföy çekme hatası:", e)
        portfolio_data = []
    return render_template('portfolio.html', portfolio=portfolio_data)

# İşlem geçmişi
@app.route('/trades')
@login_required
def trades():
    try:
        trades_data = get_ibkr_trades()
    except Exception as e:
        print("Trade çekme hatası:", e)
        trades_data = []
    return render_template('history.html', trades=trades_data)

# Performans
@app.route('/performance')
@login_required
def performance():
    return render_template('performance.html')

# Copy Trade
@app.route('/copy-trade')
@login_required
def copy_trade():
    return render_template('copy_trade.html')

# Hataları konsola göster
# KAPATILDI! Çünkü Flask debug zaten detay veriyor

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



