import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import streamlit.components.v1 as components
import tradermade as tm

tm.set_rest_api_key('Your API Key')

# Initialize default values in session state
if "category" not in st.session_state:
    st.session_state.category = "Forex"
if "currency" not in st.session_state:
    st.session_state.currency = "EURUSD"
if "data_fetched" not in st.session_state:
    st.session_state.data_fetched = False


def get_data_raw(currency_pair, start_time, end_time, interval='minute'):
    """
    Fetches minute-level OHLC data for a given currency pair and time range.

    Args:
        currency_pair (str): The currency pair (e.g., 'EURUSD').
        start_time (str): Start time in 'YYYY-MM-DD-HH:MM' format.
        end_time (str): End time in 'YYYY-MM-DD-HH:MM' format.
        interval (str): Data interval; default is 'minute'.

    Returns:
        pd.DataFrame: DataFrame containing the OHLC data.
    """
    print(end_time)
    try:
        # Fetch data using TraderMade SDK
        data = tm.timeseries(
            currency=currency_pair,
            start=start_time,
            end=end_time,
            interval=interval,
            period=30,
            fields=["open", "high", "low", "close"]
        )
        # print(data)
        # Print the response to see its structure
        # print("API Response:", data)

        # Convert the response directly into a DataFrame
        df = pd.DataFrame(data)
        df['volume'] = df['close']
        # Convert the 'date' column to datetime if it exists
        df = df.replace(0, np.nan)
        df = df.dropna()
        df.set_index("date", inplace=True)
        df = np.round(df, 4)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        # Sort the DataFrame by index
        df.sort_index(inplace=True)
        return df


    except KeyError as e:
        print(f"KeyError: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of a general error

# Utility functions
def last_work_date(date, format):
    if datetime.datetime.strptime(date, "%Y-%m-%d").weekday() == 6:
        return (datetime.datetime.strptime(date, "%Y-%m-%d")-relativedelta(days=2)).strftime(format)
    elif datetime.datetime.strptime(date, "%Y-%m-%d").weekday() == 0:
        return (datetime.datetime.strptime(date, "%Y-%m-%d")-relativedelta(days=3)).strftime(format)
    else:
        return (datetime.datetime.strptime(date, "%Y-%m-%d")-relativedelta(days=1)).strftime(format)



def get_rd(currency):
    od_list = ["UKOIL", "OIL", "XAGUSD","EVAUST","LUNUST",'LTCUST','XMRUST']
    od2_list = ["JPY"]
    od3_list = ["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "BABA", "TWTR", "BAC", "BIDU", 
    'XAUUSD','SOLUST','BNBUST','BCHUST','DSHUST','EGLUST']
    od4_list = ["UK100", "SPX500","FRA40", "GER30","JPN225","NAS100","USA30", "HKG33", 
    "AUS200","BTC","BTCUST",'ETHUSD',"ETHUST"]
    cfd_list = ["EURNOK", "EURSEK", "USDSEK","USDNOK","NEOUST","ETCUST","DOTUST", "UNIUST"]
    if currency in od_list or currency[3:6] in od2_list:
        ad = .01
        rd = 2
    elif currency in od3_list:
        ad = 0.1
        rd = 1
    elif currency in od4_list:
        ad = 2
        rd = 0
    elif currency in cfd_list:
        ad = .001
        rd = 3
    else:
        ad = 0.0001
        rd = 4
    return rd, ad

def get_ad(ad, max, min):
    if (max-min) > ad*2000:
        return ad*50
    if (max-min) > ad*1000:
        return ad*20
    if (max-min) > ad*300:
        return ad*5
    elif (max-min) > ad*100:
        return ad*2
    else:
        return ad


def get_data_MP(g, p, f, F, cur, st, ed):
    df = get_data_raw(cur, st, ed)
    
    
    return df

def midmax_idx(array):
    if len(array) == 0:
        return None

    # Find candidate maxima
    # maxima_idxs = np.argwhere(array.to_numpy() == np.amax(array.to_numpy()))[:, 0]
    maxima_idxs = np.argwhere(array == np.amax(array))[:,0]
    if len(maxima_idxs) == 1:
        return maxima_idxs[0]
    elif len(maxima_idxs) <= 1:
        return None

    # Find the distances from the midpoint to find
    # the maxima with the least distance
    midpoint = len(array) / 2
    v_norm = np.vectorize(np.linalg.norm)
    maximum_idx = np.argmin(v_norm(maxima_idxs - midpoint))
    return maxima_idxs[maximum_idx]

def calculate_value_area(poc_volume, target_vol, poc_idx, mp):
    min_idx = poc_idx
    max_idx = poc_idx
    while poc_volume < target_vol:
        last_min = min_idx
        last_max = max_idx

        next_min_idx = np.clip(min_idx - 1, 0, len(mp) - 1)
        next_max_idx = np.clip(max_idx + 1, 0, len(mp) - 1)

        low_volume = mp.iloc[next_min_idx].vol if next_min_idx != last_min else None
        high_volume = mp.iloc[next_max_idx].vol if next_max_idx != last_max else None

        if not high_volume or (low_volume and low_volume > high_volume):
            poc_volume += low_volume
            min_idx = next_min_idx
        elif not low_volume or (high_volume and low_volume <= high_volume):
            poc_volume += high_volume
            max_idx = next_max_idx
        else:
            break
    return mp.iloc[min_idx].value, mp.iloc[max_idx].value
mp_dict = {
      "0000": "A",
      "0030": "B",
      "0100": "C",
      "0130": "D",
      "0200": "E",
      "0230": "F",
      "0300": "G",
      "0330": "H",
      "0400": "I",
      "0430": "J",
      "0500": "K",
      "0530": "L",
      "0600": "M",
      "0630": "N",
      "0700": "O",
      "0730": "P",
      "0800": "Q",
      "0830": "R",
      "0900": "S",
      "0930": "T",
      "1000": "U",
      "1030": "V",
      "1100": "W",
      "1130": "X",
      "1200": "a",
      "1230": "b",
      "1300": "c",
      "1330": "d",
      "1400": "e",
      "1430": "f",
      "1500": "g",
      "1530": "h",
      "1600": "i",
      "1630": "j",
      "1700": "k",
      "1730": "l",
      "1800": "m",
      "1830": "n",
      "1900": "o",
      "1930": "p",
      "2000": "q",
      "2030": "r",
      "2100": "s",
      "2130": "t",
      "2200": "u",
      "2230": "v",
      "2300": "w",
      "2330": "x",
    }

# Updated cal_mar_pro function
def cal_mar_pro(currency, study, freq, period, mode, fp, mp_st, mp_ed, date):
    st = datetime.datetime.strptime(mp_st, "%Y-%m-%d-%H:%M")
    print(currency, mp_st, mp_ed)
    # try:
    rf = get_data_MP("M", str(freq), "%Y-%m-%d-%H:%M" , "%Y-%m-%d-%H:%M",currency, mp_st, mp_ed)
    hf = rf.copy()
    last_price = rf.iloc[-1]["close"]

    rf = rf[["high","low"]]
    rf.index = pd.to_datetime(rf.index)
    #rf = rf[:96]
    rd, ad = get_rd(currency)
    max = round(rf.high.max(), rd)
    min = round(rf.low.min(), rd)
    ad = get_ad(ad, max, min)
    try:
      x_data = np.round(np.arange(min, max, ad).tolist(), rd)
    except:
      print("MP loop failed", currency)
    # x_data = x_data[::-1]
    y_data= []
    z_data = []
    y_data1= []
    z_data1 = []
    tocount1 = 0
    for item in x_data:
        alpha = ""
        alpha1 = ""
        alpha2 = ""
        for i in range(len(rf)):
            if rf.index[i] < date:
                if round(rf.iloc[i]["high"], rd) >= item >= round(rf.iloc[i]["low"], rd):
                    alpha += mp_dict[rf.index[i].strftime("%H%M")]
            elif rf.index[i] >= date:
                if round(rf.iloc[i]["high"], rd) >= item >= round(rf.iloc[i]["low"], rd):
                    alpha1 += mp_dict[rf.index[i].strftime("%H%M")]
        tocount1 += len(alpha1)
        y_data.append(len(alpha))
        y_data1.append(len(alpha1))
        z_data.append(alpha)
        z_data1.append(alpha1)
    # y_data = y_data[::-1]
    # y_data1 = y_data1[::-1]
    mp = pd.DataFrame([x_data, y_data1]).T
    mp = mp[::-1]
    mp = mp.rename(columns={0:"value",1:"vol"})
    #poc_idx = midmax_idx(mp.vol)
    poc_idx = midmax_idx(mp.vol.values)
    poc_vol = mp.iloc[poc_idx].vol
    poc_price = mp.iloc[poc_idx].value
    target_vol = 0.7*tocount1


    value_high,value_low = calculate_value_area(poc_vol, target_vol, poc_idx, mp)
    print("Value area",tocount1, 0.7*tocount1)


    return x_data, y_data,y_data1, z_data, z_data1, value_high, value_low, poc_price, last_price, hf
# Streamlit code to take input
st.set_page_config(layout="wide")
st.title("Market Profile Dashboard")

# currency = st.sidebar.text_input("Enter Currency Pair (e.g., EURUSD):", "EURUSD")
category = st.sidebar.selectbox("Select Category", ["CFD", "Forex"], index=["CFD", "Forex"].index(st.session_state.category))
item_list = tm.cfd_list() if category == "CFD" else ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "EURNOK", "USDJPY", "EURGBP", "BTCUSD", "USDCHF", "NZDUSD", "USDINR", "USDZAR", "ETHUSD", "EURSEK"]

# Ensure item_list is a list and contains the default currency
if isinstance(item_list, list) and st.session_state.currency in item_list:
    index = item_list.index(st.session_state.currency)
else:
    index = 0  # Default to the first item if the currency is not in the list

currency = st.sidebar.selectbox("Select an Item", item_list, index=index)
study = st.sidebar.selectbox("Select Study Type:", ["MP"])
date = st.sidebar.date_input("Select Date")
# print(date)
# Subtract one day using relativedelta to get the previous day at 00:00 hours
mp_st = last_work_date(date.strftime('%Y-%m-%d'), '%Y-%m-%d-00:00')
if date != datetime.datetime.now().date():
    mp_ed = date.strftime('%Y-%m-%d-23:59')
else:
    mp_ed = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M')    
# Convert to string format
# mp_st = previous_day.strftime("%Y-%m-%d-%H:%M")
freq = st.sidebar.selectbox("Select Minutes per period:", [30])
period = st.sidebar.selectbox("Select periods:", [24])
mode = st.sidebar.selectbox("Select Mode:", ["tpo"])
fp = int((60/int(freq))*period)

if date.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
    st.warning("Please select a weekday (Monday to Friday). Weekends are not allowed.")
    st.stop()  # Stop the app execution if the date is a weekend

# Check if the button has been clicked using session state
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False

# Create the Market Profile chart only when the button is clicked
if st.sidebar.button("Get Market Profile"):
    st.session_state.button_clicked = True

if st.session_state.button_clicked:
    print(currency, study, freq, period, mode, fp, mp_st)
    x_data, y_data,y_data1, z_data, z_data1, value_high, value_low, poc_price, last_price, hf = cal_mar_pro(currency, study, freq, period, mode, fp, mp_st,mp_ed, date)
    # Separate data for previous day and current day
    previous_day_prices = x_data
    current_day_prices = x_data
    previous_day_counts = y_data
    current_day_counts = y_data1

    # print(x_data,z_data,z_data1,value_high, value_low, poc_price, last_price)
    # Create the Market Profile chart for previous day
    # print(z_data, hf)
    candlestick = go.Candlestick(
        x=hf.index,
        open=hf['open'],
        high=hf['high'],
        low=hf['low'],
        close=hf['close'],
        name=f'{currency} Candlestick Chart',
    )
    tpo_dict = {}
    for i in range(len(hf.index)):
        # Map index to date, using '00:00' hours formatting if necessary
        tpo_dict[i] = hf.index[i]
    previous_day_dates = []
    current_day_dates = [] 
    for i in previous_day_counts:
        previous_day_dates.append(tpo_dict[i])
    for i in current_day_counts:
        current_day_dates.append(tpo_dict[i])

    # Create a vertical bar chart using the same x-axis (dates) and y-axis (volume)
    bar_chart = go.Bar(
        x=previous_day_dates,  # Use the same dates for x-axis
        y=previous_day_prices,  # Volume data for y-axis
        orientation='h',
        name="TPO Count previous day",
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(color='rgba(50, 171, 96, 1.0)', width=1)
        ),
        opacity=0.5,  # Adjust opacity to make both charts visible
        hoverinfo='skip'
    )
    bar_chart2 = go.Bar(
            x=current_day_dates,  # Use the same dates for x-axis
            y=current_day_prices,  # Volume data for y-axis
            orientation='h',
            name=f"TPO Count {date}",
            marker=dict(
            color='rgba(100, 149, 237, 0.6)',
            line=dict(color='rgba(100, 149, 237, 1.0)', width=1),
        ),
        opacity=0.5,  # Adjust opacity to make both charts visible
        hoverinfo='skip'
    )


    # Initialize the figure and add both traces
    fig1 = go.Figure()
    fig1.add_trace(candlestick)
    fig1.add_trace(bar_chart)
    fig1.add_trace(bar_chart2)
    print(y_data[0],y_data[-1:], poc_price)
    num_ticks = 6  # Number of ticks to display
    tick_indices = np.linspace(0, len(hf.index) - 1, num_ticks, dtype=int)
    tickvals = [hf.index[i] for i in tick_indices]
    ticktext = [hf.index[i] for i in tick_indices]

    # Update x-axis to show fewer date labels
    fig1.update_xaxes(
        tickvals=tickvals,  # Specify which dates to show
        ticktext=ticktext,  # Specify the labels for those dates
        tickangle=0,  # Keep the tick labels horizontal
        title_text='Date',
        showgrid=True,
    )
    fig1.update_yaxes(
        showgrid=True,
    )
    # Update layout for the combined chart
    fig1.update_layout(
        title=f'{currency} Candlestick Chart with TPO Bars',
        xaxis_title='Date/TPO Count',
        yaxis_title='Price',
        yaxis=dict(range=[x_data[0], x_data[-1]]),  # Reverse the y-axis
        height=600,
        xaxis=dict(
            type='category',  # Use 'category' type to skip missing dates
            categoryorder='category ascending',  # Order categories in ascending order
            showgrid=True,
        ),
        xaxis_rangeslider_visible=False  # Hide the range slider
    )

    # Create the Market Profile chart for current day
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=previous_day_counts,  # Count on the x-axis
        y=previous_day_prices,  # Price levels on the y-axis
        orientation='h',
        name=f"TPO Count Previous day",
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(color='rgba(50, 171, 96, 1.0)', width=1)
        ),
        opacity=0.5
    ))
    
    fig2.add_trace(go.Bar(
        x=current_day_counts,  # Count on the x-axis
        y=current_day_prices,  # Price levels on the y-axis
        orientation='h',
        name=f"TPO Count {date}",
        marker=dict(
            color='rgba(100, 149, 237, 0.6)',
            line=dict(color='rgba(100, 149, 237, 1.0)', width=1),
        ),
    ))
    fig2.update_xaxes(
        showgrid=True,
    )
    fig2.update_yaxes(
        showgrid=True,
    )
    fig2.update_layout(
        title=f"{currency} Two-day Market Profile",
        xaxis_title="TPO Count",
        yaxis_title="Price Levels",
        template="plotly_white",
        height=600,
        width=600
    )

    # Create two columns to display charts side by side
    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(fig1, use_container_width=True)  # Adjusts the chart to fit the column width

    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    style = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Courier New', Courier, monospace;  /* Monospaced font */
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
        white-space: nowrap;  /* Ensure no text wrapping */
        font-weight: bold;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;  /* Light gray background for even rows */
    }
    tr:hover {
        background-color: #f1f1f1;  /* Highlight row on hover */
    }
    </style>"""

    html_table = style
    html_table += "<table style='width:100%; border: 1px solid black; font-size: 12px; border-collapse: collapse;font-family: 'Courier New', Courier, monospace;'>"
    html_table += "<tr><th style='border: 1px solid black; padding: 2px;'>Prices</th>"
    html_table += "<th style='border: 1px solid black;padding: 2px;'>Previous Day</th>"
    html_table += f"<th style='border: 1px solid black;padding: 2px;'>{date}</th></tr>"

    # Populate the table rows
    for x, z, z1 in zip(reversed(x_data), reversed(z_data), reversed(z_data1)):
        if x in [value_low, poc_price, value_high]:
            html_table += f"<tr><td style='color:#FF6961; border: 1px solid black; padding: 0px;'>{x}</td>"
            html_table += f"<td style='color:#FF6961; border: 1px solid black; padding: 0px;'>{z}</td>"
            html_table += f"<td style='color:#FF6961; border: 1px solid black; padding: 0px;'>{z1}</td></tr>"
        else:       
            html_table += f"<tr><td style='border: 1px solid black; padding: 0px;'>{x}</td>"
            html_table += f"<td style='border: 1px solid black; padding: 0px;'>{z}</td>"
            html_table += f"<td style='border: 1px solid black; padding: 0px;'>{z1}</td></tr>"

    html_table += "</table>"
    
    html_table2 = style
    html_table2 += f"""
    <table style='width:100%; border: 1px solid black; border-collapse: collapse; font-size: 10px;'>
        <tr>
            <th style='border: 1px solid black; padding: 2px;'>Letter</th>
            <th style='border: 1px solid black; padding: 2px;'>Period</th>
        </tr>
    """
    
    # Populate the second table rows in reverse order or different formatting
    for letter, period in mp_dict.items():
        html_table2 += f"""
        <tr>
            <td style='border: 1px solid black; padding: 2px;'>{letter}</td>
            <td style='border: 1px solid black; padding: 2px;'>{period}</td>
        </tr>
        """

    html_table2 += f"</table>"

    html_table3 = style
    html_table3 += f"""
    <table style='width:100%; border: 1px solid black; border-collapse: collapse; font-size: 10px;'>
        <tr>
            <th style='border: 1px solid black; padding: 2px;'>Key Prices</th>
            <th style='border: 1px solid black; padding: 2px;'>Values</th>
        </tr>
    """
    
    html_table3 += f"""
        <tr>
            <td style='border: 1px solid black; padding: 2px;'>Value Area High</td>
            <td style='border: 1px solid black; padding: 2px;'>{value_high}</td>
        </tr>
        <tr>
            <td style='border: 1px solid black; padding: 2px;'>Point of Control (POC)</td>
            <td style='border: 1px solid black; padding: 2px;'>{poc_price}</td>
        </tr>
        <tr>
            <td style='border: 1px solid black; padding: 2px;'>Value Area Low</td>
            <td style='border: 1px solid black; padding: 2px;'>{value_low}</td>
        </tr>
        </table>
        """
    #print(html_table2)
    col3, col4 = st.columns([2, 2])
    with col1:
        components.html(html_table, height=2000, scrolling=True)
    with col2:
        components.html(html_table3,height=90, scrolling=True)
        components.html(html_table2, height=1200, scrolling=True)



