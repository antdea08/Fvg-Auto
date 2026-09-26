import ccxt, requests, os, time, json
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

COINS = [
    "TAO/USDT","CAKE/USDT","ETHFI/USDT","LINK/USDT","JUP/USDT",
    "NEAR/USDT","LDO/USDT","SUI/USDT","INJ/USDT","AVAX/USDT",
    "HYPE/USDT","ZEC/USDT","PENDLE/USDT","ENA/USDT","ADA/USDT",
    "ORDI/USDT","WLD/USDT","HBAR/USDT","TRUMP/USDT","UNI/USDT"
]

# BITGET WAJIB PAKE INI
exchange = ccxt.bitget({
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

def tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=10)
    except: pass

def get_bullish_fvg(c):
    valid=[]
    if len(c)<50: return valid
    for i in range(2, len(c)-25):
        high1 = c[i-2][2]
        low3 = c[i][3]
        if high1 < low3 and (low3-high1)/low3*100 > 0.15:
            closed=False
            for j in range(i+1, len(c)-1):
                if high1 <= c[j][4] <= low3:
                    closed=True; break
            if not closed:
                valid.append((high1, low3))
    return valid[-3:]

def load():
    try: return json.load(open("sent.json"))
    except: return {}
def save(d): json.dump(d, open("sent.json","w"))

# INI KUNCINYA BITGET
print("Loading markets bitget...")
exchange.load_markets()
print(f"BOT START BULLISH ONLY BITGET - {datetime.now()}")

sent=load()

for S in COINS:
    try:
        # Bitget kadang delay, kasih try 2x
        o1 = exchange.fetch_ohlcv(S,'1h', limit=100)
        time.sleep(0.8)
        o4 = exchange.fetch_ohlcv(S,'4h', limit=100)
        time.sleep(0.8)

        if not o1 or not o4 or len(o1)<30 or len(o4)<30:
            print(f"{S} ohlcv kosong {len(o1)}/{len(o4)} skip")
            continue

        p1=o1[-2][4]; p4=o4[-2][4]
        f1=get_bullish_fvg(o1); f4=get_bullish_fvg(o4)

        print(f"CHECK {S} | Price {p1} | H1:{len(f1)} | H4:{len(f4)}")

        for bot,top in f1:
            key=f"{S}_H1_{bot}"
            if bot <= p1 <= top and key not in sent:
                tele(f"🟢 *{S} BULLISH FVG H1 (BITGET)*\nPrice: {p1}\nFVG: {bot:.4f}-{top:.4f}")
                sent[key]=1; save(sent); break

        for bot,top in f4:
            key=f"{S}_H4_{bot}"
            if bot <= p4 <= top and key not in sent:
                tele(f"🔵 *{S} BULLISH FVG H4 (BITGET)*\nPrice: {p4}\nFVG: {bot:.4f}-{top:.4f}")
                sent[key]=1; save(sent); break

    except Exception as e:
        print(f"ERROR {S}: {e}")
        continue

print("FINISH")
