import ccxt, requests, os, time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

COINS = ["TAO/USDT","CAKE/USDT","ETHFI/USDT","LINK/USDT","JUP/USDT","NEAR/USDT","LDO/USDT","SUI/USDT","INJ/USDT","AVAX/USDT","HYPE/USDT","ZEC/USDT","PENDLE/USDT","ENA/USDT","ADA/USDT","ORDI/USDT","WLD/USDT","HBAR/USDT","TRUMP/USDT","UNI/USDT"]

exchange = ccxt.binance()

def send_tele(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"})

def get_fvg(candles):
    zones=[]
    for i in range(2,len(candles)):
        low_i, high_i = candles[i][3], candles[i][2]
        low_2, high_2 = candles[i-2][3], candles[i-2][2]
        if low_i > high_2: zones.append({'type':'BULL','bot':high_2,'top':low_i})
        if high_i < low_2: zones.append({'type':'BEAR','bot':high_i,'top':low_2})
    return zones[-15:]

for SYMBOL in COINS:
    try:
        h1 = exchange.fetch_ohlcv(SYMBOL, '1h', limit=100)
        h4 = exchange.fetch_ohlcv(SYMBOL, '4h', limit=100)
        price = h1[-1][4]

        fvg_h1 = get_fvg(h1)
        fvg_h4 = get_fvg(h4)

        in_h1 = next((z for z in fvg_h1 if z['bot'] <= price <= z['top']), None)
        in_h4 = next((z for z in fvg_h4 if z['bot'] <= price <= z['top']), None)

        if in_h1 and in_h4 and in_h1['type'] == in_h4['type']:
            send_tele(f"🔥 *{SYMBOL} MASUK FVG H1+H4* {in_h1['type']}\nPrice: {price}")
        elif in_h1:
            send_tele(f"⚠️ *{SYMBOL} MASUK FVG H1* {in_h1['type']}\nPrice: {price}")

        time.sleep(0.3)
    except Exception as e:
        print(f"{SYMBOL} {e}")
        continue

print("done")
