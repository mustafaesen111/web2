from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/portfolio')
def portfolio():
    # Örnek sabit veri, gerçek veriyi veritabanından veya API'den çekeceksin
    portfolio = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'quantity': 50, 'avg_price': 145.0, 'current_price': 150.0, 'pl': 250},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'quantity': 10, 'avg_price': 600.0, 'current_price': 700.0, 'pl': 1000},
    ]
    return render_template('portfolio.html', portfolio=portfolio)

@app.route('/performance')
def performance():
    # Örnek veri
    chart_labels = ['Jan', 'Feb', 'Mar', 'Apr']
    chart_data = [2.5, 3.0, -1.2, 4.0]
    return render_template('performance.html', chart_labels=chart_labels, chart_data=chart_data)

@app.route('/copy-trade')
def copy_trade():
    # Örnek user kopyalama durumu
    user = {'copy_enabled': False}
    return render_template('copy_trade.html', user=user)

@app.route('/subscribe')
def subscribe():
    stripe_public_key = 'your_stripe_public_key_here'  # Gumroad ile değiştireceğiz
    return render_template('subscribe.html', stripe_public_key=stripe_public_key)

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
