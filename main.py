import yfinance as yf
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 20 KOIN LU
COINS = [
    "TAO-USD", "CAKE-USD", "ETHFI-USD", "LINK-USD", "JUP-USD",
    "NEAR-USD", "LDO-USD", "SUI-USD", "INJ-USD", "AVAX-USD",
    "HYPE-USD", "ZEC-USD", "PENDLE-USD", "ENA-USD", "ADA-USD",
    "ORDI-USD", "WLD-USD", "HBAR-USD", "TRUMP-USD", "UNI-USD"
]

def send_tele(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def get_fvg(df):
    zones = []
    for i in range(2, len(df)):
        # FVG BULLISH: Low candle sekarang > High 2 candle lalu
        if df['Low'].iloc[i] > df['High'].iloc[i-2]:
            zones.append({'type': 'BULL', 'top': float(df['Low'].iloc[i]), 'bot': float(df['High'].iloc[i-2])})
        # FVG BEARISH: High candle sekarang < Low 2 candle lalu
        if df['High'].iloc[i] < df['Low'].iloc[i-2]:
            zones.append({'type': 'BEAR', 'top': float(df['Low'].iloc[i-2]), 'bot': float(df['High'].iloc[i])})
    return zones[-15:]

for SYMBOL in COINS:
    try:
        h1 = yf.download(SYMBOL, period="10d", interval="60m", progress=False, auto_adjust=True)
        h4 = yf.download(SYMBOL, period="1mo", interval="240m", progress=False, auto_adjust=True)
        if len(h1) < 20 or len(h4) < 20:
            continue

        price = float(h1['Close'].iloc[-1])
        fvg_h1 = get_fvg(h1)
        fvg_h4 = get_fvg(h4)

        in_h1 = next((z for z in fvg_h1 if z['bot'] <= price <= z['top']), None)
        in_h4 = next((z for z in fvg_h4 if z['bot'] <= price <= z['top']), None)

        if in_h1 and in_h4 and in_h1['type'] == in_h4['type']:
            send_tele(f"🔥 *{SYMBOL} - MASUK FVG H1 + H4*\nType: {in_h1['type']}\nPrice: {price}\nH1: {in_h1['bot']:.4f}-{in_h1['top']:.4f}\nH4: {in_h4['bot']:.4f}-{in_h4['top']:.4f}")
        elif in_h1:
            send_tele(f"⚠️ *{SYMBOL} - MASUK FVG H1*\nType: {in_h1['type']}\nPrice: {price}\nZone: {in_h1['bot']:.4f}-{in_h1['top']:.4f}")
        elif in_h4:
            send_tele(f"⚠️ *{SYMBOL} - MASUK FVG H4*\nType: {in_h4['type']}\nPrice: {price}\nZone: {in_h4['bot']:.4f}-{in_h4['top']:.4f}")

        time.sleep(1)
    except Exception as e:
        print(f"{SYMBOL} error {e}")
        continue

print("done scan 20 coin")
