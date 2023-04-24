import ccxt
from config import API_KEY, API_SECRET

# Set up the exchange
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})


markets = exchange.load_markets()

for m in markets:
    print(m)
