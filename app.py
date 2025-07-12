from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

# Flask-Login ayarları
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Kullanıcı Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Ana Sayfa
@app.route('/')
def home():
    return render_template('home.html')


# Kayıt
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful. You can now log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Giriş
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')


# Çıkış
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


# Diğer sayfalar
@app.route('/portfolio')
@login_required
def portfolio():
    return render_template('portfolio.html')


@app.route('/performance')
@login_required
def performance():
    return render_template('performance.html')


@app.route('/copy-trade', methods=['GET', 'POST'])
@login_required
def copy_trade():
    return render_template('copy_trade.html')


@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    return render_template('subscribe.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



