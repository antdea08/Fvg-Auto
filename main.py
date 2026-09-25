import ccxt, requests, os, time, json
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COINS = ["TAO/USDT","CAKE/USDT","ETHFI/USDT","LINK/USDT","JUP/USDT","NEAR/USDT","LDO/USDT","SUI/USDT","INJ/USDT","AVAX/USDT","HYPE/USDT","ZEC/USDT","PENDLE/USDT","ENA/USDT","ADA/USDT","ORDI/USDT","WLD/USDT","HBAR/USDT","TRUMP/USDT","UNI/USDT"]

exchange = ccxt.binance({
    'enableRateLimit': True,
})

def tele(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":m,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def get_fvg_valid(candles):
    valid=[]
    if len(candles) < 30: return valid
    for i in range(2, len(candles)-20):
        bot = candles[i-2][2]
        top = candles[i][3]
        if top > bot and (top-bot)/top*100 > 0.2:
            closed=False
            for j in range(i+1, len(candles)-1):
                if bot <= candles[j][4] <= top:
                    closed=True; break
            if not closed:
                valid.append((bot,top))
    return valid[-3:]

def load():
    try: return json.load(open("sent.json"))
    except: return {}
def save(d): json.dump(d, open("sent.json","w"))

sent=load()

for S in COINS:
    try:
        o1 = exchange.fetch_ohlcv(S,'1h',limit=100)
        time.sleep(0.5)
        o4 = exchange.fetch_ohlcv(S,'4h',limit=100)
        time.sleep(0.5)

        if not o1 or not o4 or len(o1) < 30 or len(o4) < 30:
            print(f"{S} data kosong, skip")
            continue

        p1 = o1[-2][4]
        p4 = o4[-2][4]

        for b,t in get_fvg_valid(o1):
            key=f"{S}_H1_{b}"
            if b <= p1 <= t and key not in sent:
                tele(f"🟢 {S} MASUK FVG H1 VALID {p1}")
                sent[key]=1; save(sent); break

        for b,t in get_fvg_valid(o4):
            key=f"{S}_H4_{b}"
            if b <= p4 <= t and key not in sent:
                tele(f"🔵 {S} MASUK FVG H4 VALID {p4}")
                sent[key]=1; save(sent); break

    except Exception as e:
        print(f"Error {S}: {e}")
        continue
