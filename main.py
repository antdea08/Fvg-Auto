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

exchange = ccxt.bitget({'enableRateLimit': True})

def tele(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode":"Markdown"}, timeout=10)
    except: pass

def get_bullish_fvg_valid(candles):
    """BULLISH FVG AJA: high[i-2] < low[i] dan belum ketutup"""
    valid = []
    if len(candles) < 50: return valid
    for i in range(2, len(candles)-20):
        # high 2 candle lalu
        high1 = candles[i-2][2]
        # low candle sekarang
        low3 = candles[i][3]

        # Bullish FVG ada gap naik
        if high1 < low3:
            gap = (low3 - high1) / low3 * 100
            if gap > 0.15: # filter gap kecil
                # cek sudah ketutup belum?
                closed = False
                for j in range(i+1, len(candles)-1):
                    # kalo ada candle yang masuk ke dalam gap = invalid
                    if candles[j][3] <= high1 or candles[j][2] <= high1:
                        # cek low nya nyentuh gap
                        if candles[j][3] < low3 and candles[j][3] > high1:
                            closed = True
                            break
                        if candles[j][2] < low3 and candles[j][2] > high1:
                            closed = True
                            break
                        if candles[j][4] >= high1 and candles[j][4] <= low3:
                            closed = True
                            break
                if not closed:
                    valid.append((high1, low3)) # bot, top
    return valid[-3:]

def load():
    try: return json.load(open("sent.json"))
    except: return {}
def save(d): json.dump(d, open("sent.json","w"))

sent = load()
print(f"BOT START BULLISH ONLY - {datetime.now()}")

for S in COINS:
    try:
        o1 = exchange.fetch_ohlcv(S, '1h', 100)
        time.sleep(0.6)
        o4 = exchange.fetch_ohlcv(S, '4h', 100)
        time.sleep(0.6)

        p1 = o1[-2][4]
        p4 = o4[-2][4]

        fvg_h1 = get_bullish_fvg_valid(o1)
        fvg_h4 = get_bullish_fvg_valid(o4)

        print(f"CHECK {S} | H1:{len(fvg_h1)} bullish | H4:{len(fvg_h4)} bullish | Price {p1}")

        for bot, top in fvg_h1:
            key = f"{S}_H1_BULL_{bot}"
            if bot <= p1 <= top and key not in sent:
                tele(f"🟢 *{S} BULLISH FVG H1*\nPrice masuk: {p1}\nFVG: {bot:.4f} - {top:.4f}\nSetup LONG")
                print(f">>> ALERT BULLISH H1 {S}")
                sent[key]=1; save(sent); break

        for bot, top in fvg_h4:
            key = f"{S}_H4_BULL_{bot}"
            if bot <= p4 <= top and key not in sent:
                tele(f"🔵 *{S} BULLISH FVG H4*\nPrice masuk: {p4}\nFVG: {bot:.4f} - {top:.4f}\nSetup LONG")
                print(f">>> ALERT BULLISH H4 {S}")
                sent[key]=1; save(sent); break

    except Exception as e:
        print(f"ERROR {S} {e}")
        continue

print("FINISH")
