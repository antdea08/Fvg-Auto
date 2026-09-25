import ccxt, requests, os, time, json
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COINS = ["TAO/USDT","CAKE/USDT","ETHFI/USDT","LINK/USDT","JUP/USDT","NEAR/USDT","LDO/USDT","SUI/USDT","INJ/USDT","AVAX/USDT","HYPE/USDT","ZEC/USDT","PENDLE/USDT","ENA/USDT","ADA/USDT","ORDI/USDT","WLD/USDT","HBAR/USDT","TRUMP/USDT","UNI/USDT"]
exchange = ccxt.bitget()

def load_sent():
    try:
        with open("sent.json","r") as f: return json.load(f)
    except: return {}
def save_sent(d):
    with open("sent.json","w") as f: json.dump(d,f)
def send_tele(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"})
def get_fvg(candles):
    z=[]
    for i in range(2,len(candles)):
        if candles[i][3] > candles[i-2][2]:
            z.append((candles[i-2][2], candles[i][3]))
    return z

sent = load_sent()
now = time.time()

for S in COINS:
    try:
        o1 = exchange.fetch_ohlcv(S,'1h',limit=100)
        o4 = exchange.fetch_ohlcv(S,'4h',limit=100)
        p = o1[-1][4]

        # CEK H1 SENDIRI
        if any(bot <= p <= top for bot,top in get_fvg(o1)[-5:]):
            if now - sent.get(f"{S}_H1",0) > 14400:
                send_tele(f"🟢 *{S} MASUK FVG BULL H1* Price: {p}")
                sent[f"{S}_H1"]=now
                save_sent(sent)

        # CEK H4 SENDIRI (PISAH)
        if any(bot <= p <= top for bot,top in get_fvg(o4)[-5:]):
            if now - sent.get(f"{S}_H4",0) > 14400:
                send_tele(f"🔵 *{S} MASUK FVG BULL H4* Price: {p}")
                sent[f"{S}_H4"]=now
                save_sent(sent)

        time.sleep(0.4)
    except:
        continue
