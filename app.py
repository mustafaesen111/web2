from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Login yöneticisi
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Bu e-posta zaten kayıtlı.")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Giriş başarılı.")
            return redirect(url_for("home"))
        else:
            flash("Hatalı giriş bilgisi.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Çıkış yapıldı.")
    return redirect(url_for("home"))


@app.route("/subscribe")
@login_required
def subscribe():
    return render_template("subscribe.html")


@app.route("/portfolio")
@login_required
def portfolio():
    if not current_user.is_subscribed:
        flash("Bu sayfaya erişmek için abone olmalısınız.")
        return redirect(url_for("subscribe"))
    return render_template("portfolio.html")


@app.route("/performance")
@login_required
def performance():
    if not current_user.is_subscribed:
        flash("Bu sayfaya erişmek için abone olmalısınız.")
        return redirect(url_for("subscribe"))
    return render_template("performance.html")


@app.route("/copy-trade")
@login_required
def copy_trade():
    if not current_user.is_subscribed:
        flash("Bu sayfaya erişmek için abone olmalısınız.")
        return redirect(url_for("subscribe"))
    return render_template("copy_trade.html")


@app.route("/ranks")
@login_required
def ranks():
    if not current_user.is_subscribed:
        flash("Bu sayfaya erişmek için abone olmalısınız.")
        return redirect(url_for("subscribe"))
    return render_template("ranks.html")


@app.route("/history")
@login_required
def history():
    if not current_user.is_subscribed:
        flash("Bu sayfaya erişmek için abone olmalısınız.")
        return redirect(url_for("subscribe"))
    return render_template("history.html")


@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


@app.route("/search")
def search():
    return render_template("search.html")


if __name__ == "__main__":
    app.run(debug=True)
