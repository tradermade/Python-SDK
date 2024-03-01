import websocket
import tradermade

try:
    import _thread as thread
except ImportError:
    import threading as thread

ws = None
_api_key = None
_symbol = 'GBPUSD'
message_callback = None  # Added callback variable


def set_ws_key(api_key):
    global _api_key
    _api_key = api_key

def set_symbols(symbol):
    global _symbol
    _symbol = symbol

def stream_data(callback):
    global message_callback
    message_callback = callback

def get_symbols():
    return _symbol

def api_key():
    return _api_key

def on_message(ws, message):
    
    # Call the callback function with the received message
    if message_callback:
        message_callback(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        cred = '{"userKey":"' + _api_key + '", "symbol":"' + _symbol + '"}'
        ws.send(cred)
    thread.start_new_thread(run, ())

def connect():
    global ws
    ws = websocket.WebSocketApp("wss://marketdata.tradermade.com/feedadv",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
