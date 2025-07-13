from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli_anahtarınız'  # Güçlü bir secret key koy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # sqlite örnek
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # is_subscribed kaldırıldı veya kullanılmayacak şekilde pasif bırakıldı

# Ana sayfa - giriş yapılmışsa gösterilecek sayfa
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return f"Merhaba, {user.email}! <a href='/logout'>Çıkış Yap</a>"
    return "Hoşgeldiniz! <a href='/login'>Giriş Yap</a> veya <a href='/signup'>Kayıt Ol</a>"

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Bu email zaten kayıtlı.", "danger")
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Kayıt başarılı. Lütfen giriş yapın.", "success")
        return redirect(url_for('login'))

    return '''
    <h2>Kayıt Ol</h2>
    <form method="POST">
        Email: <input type="email" name="email" required><br>
        Şifre: <input type="password" name="password" required><br>
        <button type="submit">Kayıt Ol</button>
    </form>
    '''

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Giriş başarılı!", "success")
            return redirect(url_for('index'))
        else:
            flash("Email veya şifre hatalı.", "danger")
            return redirect(url_for('login'))

    return '''
    <h2>Giriş Yap</h2>
    <form method="POST">
        Email: <input type="email" name="email" required><br>
        Şifre: <input type="password" name="password" required><br>
        <button type="submit">Giriş Yap</button>
    </form>
    '''

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Çıkış yapıldı.", "info")
    return redirect(url_for('index'))

# Hata yakalama (basit)
@app.errorhandler(500)
def internal_error(error):
    return f"Sunucu hatası: {error}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

