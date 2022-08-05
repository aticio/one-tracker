import websocket
import json
from datetime import datetime
import requests
import time

BINANCE_WEBSOCKET_ADDRESS = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"

PRICE_DATA = {}
WATCHLIST = []

def main():
    exchange_info = get_exchange_info()
    pairs = get_pairs(exchange_info)
    for pair in pairs:
        PRICE_DATA[pair] = []
    init_stream()


def get_pairs(exchange_info):
    pairs = []
    for symbol in exchange_info["symbols"]:
        pairs.append(symbol["symbol"])
    return pairs

def get_exchange_info():
    response = requests.get(EXCHANGE_INFO)
    exchange_info = response.json()
    return exchange_info


# Websocket functions
def init_stream():
    w_s = websocket.WebSocketApp(
        BINANCE_WEBSOCKET_ADDRESS,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
        )
    w_s.on_open = on_open
    w_s.run_forever()


def on_error(w_s, error):
    print(error)


def on_close(w_s, close_status_code, close_msg):
    print("closing websocket connection, initiating again...")
    init_stream()


def on_open(w_s):
    print("websocket connection opened...")


def on_message(w_s, message):
    global PRICE_DATA
    global WATCHLIST
    ticker_data = json.loads(message)

    for t in ticker_data:
        if t['s'] == 'ALPACABUSD':
            print(t['s'], t['c'], t['v'])
        # Test comment 1
        if "BUSD" in t["s"]:
            if len(PRICE_DATA[t["s"]]) == 3600:
                PRICE_DATA[t["s"]].pop(0)
            PRICE_DATA[t["s"]].append(t["c"])
            if t['s'] not in WATCHLIST:
                anomaly = check_anomaly(PRICE_DATA[t["s"]])
                if anomaly:
                    WATCHLIST.append(t['s'])
                    print(time.ctime(), t["s"], t["c"])
                    f = open("anomaly.txt", "a")
                    f.write(time.ctime() + " - " + t["s"] + " - " + t["c"] + "\n")
                    f.close()


def check_anomaly(prices):
    anomaly = False
    for p in prices[60:]:
        if float(prices[-1]) > (float(p) + (float(p) * 0.1)):
            anomaly = True
            break
    return anomaly


if __name__ == "__main__":
    main()