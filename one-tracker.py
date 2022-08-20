import websocket
import json
from datetime import datetime, timedelta
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
        if "BUSD" in t["s"] and "USDT" not in t["s"]:
            PRICE_DATA[t["s"]].append((t["E"], t["c"]))
            now = int(PRICE_DATA[t["s"]][-1][0])
            then = int(PRICE_DATA[t["s"]][0][0])           
            now_dt = datetime.fromtimestamp(int(now)/1000)
            then_dt = datetime.fromtimestamp(int(then)/1000)

            delta = abs(int((now_dt-then_dt).total_seconds()))
            if delta <= 600:
                if t['s'] not in WATCHLIST:
                    anomaly = check_anomaly(PRICE_DATA[t["s"]])
                    if anomaly:
                        WATCHLIST.append(t['s'])
                        print(time.ctime(), t["s"], t["c"])
                        f = open("anomaly.txt", "a")
                        f.write(time.ctime() + " - " + t["s"] + " - " + t["c"] + "\n")
                        f.close()
            else:                    
                for tp in PRICE_DATA[t["s"]]:
                    first_dt = datetime.fromtimestamp(int(tp[0])/1000)
                    current_delta = abs(int((now_dt-first_dt).total_seconds()))
                    if current_delta > 600:
                            PRICE_DATA[t["s"]].remove(tp)


def check_anomaly(price_data):
    anomaly = False
    anomaly_area = []
    distance_area = []
    
    now = int(price_data[-1][0])
    now_dt = datetime.fromtimestamp(int(now)/1000)

    for pd in price_data:
        current_dt = datetime.fromtimestamp(int(pd[0])/1000)
        current_delta = abs(int((now_dt-current_dt).total_seconds()))
        if current_delta < 180 and current_delta > 60:
            anomaly_area.append(pd)

    for pd in price_data:
        current_dt = datetime.fromtimestamp(int(pd[0])/1000)
        current_delta = abs(int((now_dt-current_dt).total_seconds()))
        if current_delta > 60:
            distance_area.append(pd)
    
    for aa in anomaly_area:
        if float(price_data[-1][1]) > (float(aa[1]) + (float(aa[1]) * 0.1)):
            anomaly = True
            break

    for da in distance_area:
        if float(price_data[-1][1]) > (float(da[1]) + (float(da[1]) * 0.2)):
            anomaly = False

    return anomaly


if __name__ == "__main__":
    main()