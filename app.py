from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # İstersen başka veritabanı kullanabilirsin
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Bunu güçlü ve gizli yapmayı unutma!

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email zaten kayıtlı.', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Geçersiz email veya şifre.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Çıkış yapıldı.', 'success')
    return redirect(url_for('home'))

# Diğer sayfa route'larını buraya ekleyebilirsin

if __name__ == '__main__':
    app.run(debug=True)

