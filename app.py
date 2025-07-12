from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('signup'))

        new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Diğer route'lar (portfolio, performance, copy_trade, subscribe vb.)
@app.route('/portfolio')
@login_required
def portfolio():
    # portföy verileri backend ile bağlanacak (şimdilik dummy)
    portfolio = []
    return render_template('portfolio.html', portfolio=portfolio)

@app.route('/performance')
@login_required
def performance():
    # performans verileri backend ile bağlanacak
    chart_labels = []
    chart_data = []
    return render_template('performance.html', chart_labels=chart_labels, chart_data=chart_data)

@app.route('/copy_trade', methods=['GET', 'POST'])
@login_required
def copy_trade():
    # copy trade sistemi backend bağlantısı yapılacak
    if request.method == 'POST':
        # ayarları kaydet
        pass
    user = current_user
    return render_template('copy_trade.html', user=user)

@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    # abonelik sistemi eklenecek
    return render_template('subscribe.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




