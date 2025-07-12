from flask import Flask, render_template, request

app = Flask(__name__)

# Örnek veri (gerçek veritabanı bağlanacak)
portfolio = [
    {"symbol": "AAPL", "name": "Apple Inc.", "quantity": 50, "avg_price": 150, "current_price": 160, "pl": 500},
    {"symbol": "TSLA", "name": "Tesla Inc.", "quantity": 10, "avg_price": 700, "current_price": 720, "pl": 200},
]

ranked_stocks = [
    {"symbol": "TSLA", "name": "Tesla Inc.", "return_percent": 20},
    {"symbol": "AAPL", "name": "Apple Inc.", "return_percent": 10},
]

trades = [
    {"date": "2025-07-01", "symbol": "AAPL", "action": "Buy", "quantity": 50, "price": 150},
    {"date": "2025-07-05", "symbol": "TSLA", "action": "Buy", "quantity": 10, "price": 700},
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/portfolio')
def portfolio_page():
    return render_template('portfolio.html', portfolio=portfolio)

@app.route('/stocks-ranks')
def stocks_ranks():
    return render_template('ranks.html', ranked_stocks=ranked_stocks)

@app.route('/trade-history')
def trade_history():
    return render_template('history.html', trades=trades)

@app.route('/performance')
def performance():
    # Grafik için örnek data
    chart_labels = ["Jan", "Feb", "Mar", "Apr", "May"]
    chart_data = [5, 10, 8, 12, 15]
    return render_template('performance.html', chart_labels=chart_labels, chart_data=chart_data)

@app.route('/copy-trade', methods=['GET', 'POST'])
def copy_trade():
    user = {"copy_enabled": False}  # Örnek kullanıcı verisi
    if request.method == 'POST':
        enabled = 'enable_copy' in request.form
        user["copy_enabled"] = enabled
        # Veritabanı update işlemi yapılacak
    return render_template('copy_trade.html', user=user)

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/search')
def search():
    q = request.args.get('q', '').lower()
    results = []
    if q:
        # Basit arama simülasyonu
        all_stocks = portfolio  # Gerçek veritabanı sorgusu yapılacak
        results = [s for s in all_stocks if q in s['symbol'].lower() or q in s['name'].lower()]
    return render_template('search.html', results=results)

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    stripe_public_key = "pk_test_..."  # Buraya gerçek Stripe/Gumroad public key gelecek
    return render_template('subscribe.html', stripe_public_key=stripe_public_key)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Giriş işlemleri yapılacak
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
