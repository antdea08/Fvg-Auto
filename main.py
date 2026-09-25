import ccxt, requests, os
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
COINS = ["TAO/USDT","CAKE/USDT","ETHFI/USDT","LINK/USDT","JUP/USDT","NEAR/USDT","LDO/USDT","SUI/USDT","INJ/USDT","AVAX/USDT","HYPE/USDT","ZEC/USDT","PENDLE/USDT","ENA/USDT","ADA/USDT","ORDI/USDT","WLD/USDT","HBAR/USDT","TRUMP/USDT","UNI/USDT"]
ex = ccxt.bitget()
def tele(m): requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":m})

def cek_fvg(candles):
    f=[]
    for i in range(2,len(candles)-1):
        if candles[i][3] > candles[i-2][2]:
            f.append((candles[i-2][2], candles[i][3]))
    return f

for S in COINS:
    o1 = ex.fetch_ohlcv(S,'1h',100)
    o4 = ex.fetch_ohlcv(S,'4h',100)
    p = o1[-2][4]
    for b,t in cek_fvg(o1)[-3:]:
        if b <= p <= t: tele(f"{S} MASUK FVG H1")
    for b,t in cek_fvg(o4)[-3:]:
        if b <= o4[-2][4] <= t: tele(f"{S} MASUK FVG H4")
