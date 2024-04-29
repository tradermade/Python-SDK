from tradermade import stream
import json
from datetime import datetime
from collections import defaultdict

ohlc_data = defaultdict(lambda: defaultdict(lambda: {'open': 0, 'high': 0, 'low': 0, 'close': 0}))
previous_interval = None
count = 0
interval = 1
format = '%Y-%m-%d %H:%M'
output_file = 'ohlc_output.txt'

def round_timestamp(timestamp, interval_minutes):
    rounded_minutes = (timestamp.minute // interval_minutes) * interval_minutes
    rounded_time = timestamp.replace(second=0, microsecond=0, minute=rounded_minutes)
    return rounded_time

def save_to_file(data):
    with open(output_file, 'a') as f:
        f.write(data + '\n')

def update_ohlc_data(current_interval, currency, mid):
    if current_interval not in ohlc_data:
        ohlc_data[current_interval] = defaultdict(lambda: {'open': mid, 'high': mid, 'low': mid, 'close': mid})
    elif currency not in ohlc_data[current_interval]:
        ohlc_data[current_interval][currency] = {'open': mid, 'high': mid, 'low': mid, 'close': mid}
    else:
        ohlc_data[current_interval][currency]['high'] = max(ohlc_data[current_interval][currency]['high'], mid)
        ohlc_data[current_interval][currency]['low'] = min(ohlc_data[current_interval][currency]['low'], mid)
        ohlc_data[current_interval][currency]['close'] = mid


def process_interval(current_interval):
    global previous_interval, count
    if len(ohlc_data) > 1:
        for currency, ohlc in ohlc_data[previous_interval].items():
            output = f"{previous_interval:<10} {currency:<10} {ohlc['open']:<10.5f} {ohlc['high']:<10.5f} {ohlc['low']:<10.5f} {ohlc['close']:<10.5f}"
            print(output)
            save_to_file(output)  
        count = 0
        del ohlc_data[previous_interval]

def process_data(data):
    global previous_interval, count
    if data != "Connected":
        try:
            data = json.loads(data)
            timestamp = datetime.fromtimestamp(int(data['ts']) / 1000)
            current_interval = round_timestamp(timestamp, interval).strftime(format)
            currency = data['symbol']
            mid = round(float((data['bid']) + float(data['ask'])) / 2, 5)
            update_ohlc_data(current_interval, currency, mid)
            process_interval(current_interval)
            if count == 0:
                previous_interval = current_interval
                count = 1
        except Exception as e:
            print(f"Error processing data: {e}")
    else:
        print("Connected to WebSocket")

stream.set_ws_key("API_key")  # Replace with your actual API key
stream.set_symbols("USDJPY,EURGBP")
stream.stream_data(process_data)
stream.connect()