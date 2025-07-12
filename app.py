from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Heroku / local veritabanı için ayar
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanı başlat
db.init_app(app)

# Tabloları oluştur
with app.app_context():
    db.create_all()


# Ana Sayfa
@app.route('/')
def home():
    return render_template('home.html')


# Kullanıcı Kaydı
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Giriş
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# Çıkış
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Diğer Sayfalar
@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/copy-trade')
def copy_trade():
    return render_template('copy_trade.html')

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')


if __name__ == '__main__':
    app.run(debug=True)


