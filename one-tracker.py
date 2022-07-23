import websocket
import json
from datetime import datetime
import requests

BINANCE_WEBSOCKET_ADDRESS = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"

price_data = []

def main():
    exchange_info = get_exchange_info()
    pairs = get_pairs(exchange_info)
    for pair in pairs:
        price_data.append({"pair": pair, "prices": []})
    print(price_data)
    # init_stream()


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


def on_close(w_s):
    print("closing websocket connection, initiating again...")
    init_stream()


def on_open(w_s):
    print("websocket connection opened...")


def on_message(w_s, message):
    ticker_data = json.loads(message)

    for t in ticker_data:
        if t["s"] == "BTCUSDT":
            timestamp = t["E"]
            dt_object = datetime.fromtimestamp(timestamp / 1000.0)

            if dt_object.second == 59:
                print(dt_object.minute, dt_object.second, t["o"], t["c"])

            if dt_object.second == 0:
                print(dt_object.minute, dt_object.second, t["o"], t["c"])

            if dt_object.second == 1:
                print(dt_object.minute, dt_object.second, t["o"], t["c"])

if __name__ == "__main__":
    main()