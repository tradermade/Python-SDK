import pandas as pd
import numpy as np 
import requests


_api_key = None
_stats = {} 
api_url = "https://marketdata.tradermade.com/api/v1/"
cfd_dict = {"UK100":"FTSE 100","GER30":"DAX 30","SPX500": "SP500","FRA40":"CAC 40", "JPN225":"Nikkei 225", 
"NAS100":"Nasdaq", "USA30":"DOW 30", "HKG33":"Hang Seng", "AUS200":"ASX200","COPPER":"Copper","UKOIL":"Brent",
"OIL":"Nymex","NATGAS":"Natural GAS","AAPL":"Apple", "FB":"Facebook", "AMZN":"Amazon","NFLX":"Netflix",
"TSLA":"Tesla","GOOGL":"Alphabet", "BABA":"Alibaba", "TWTR":"Twitter","BAC":"Bank of America","BIDU":"Baidu"}

cfd_crct = {"UK100U":"UK100","GER30U":"GER30","FRA40U":"FRA40","USA30U":"USA30", "HKG33U":"HKG33","UKOILU":"UKOIL",
"OILUSD":"OIL","AAPLUS":"AAPL", "FBUSD":"FB", "AMZNUS":"AMZN","NFLXUS":"NFLX",
"TSLAUS":"TSLA","GOOGLU":"GOOGL", "BABAUS":"BABA", "TWTRUS":"TWTR","BACUSD":"BAC","BIDUUS":"BIDU"}

def set_rest_api_key(api_key):
    global _api_key
    _api_key = api_key

def api_key():
    return _api_key

def get_stats(): 
    try:
      allowed = _stats["X-RateLimit-Limit"]
      remaining = _stats["X-RateLimit-Remaining"]
      resets = _stats["X-RateLimit-Reset"]
      return {"allowance":allowed,"remaining": remaining,"resets":resets}
    except:
      return None

def get_rest_api_key():
    return api_key

def get_api_usage():
    return usage

def currency_list():
    if _api_key == None:
      return "please set your apikey using function set_rest_api_key"
    df = pd.read_json("https://marketdata.tradermade.com/api/v1/live_currencies_list?api_key="+_api_key)
    df = df[["available_currencies"]]
    df = df.reset_index()
    return df
  
def cfd_list():
    df = pd.DataFrame.from_dict(list(cfd_dict.items()),orient='columns', dtype=None, columns=None)
    df = df.rename(columns={0:"index",1:"intrument"})

    return df

def live(currency,fields=None):
  if _api_key == None:
      return "please set your apikey using function set_rest_api_key"
  if type(fields) != type([]) and fields != None:
     return {"error":"fields must be a list, ex ['bid','ask']"}
  url = api_url+"live"

  querystring = {"currency":currency,"api_key":_api_key}

  response = requests.get(url, params=querystring)  
  #print(response.json())
  column_list = ["instrument","timestamp"]
  try:
    df = pd.DataFrame(response.json()["quotes"])
  except:
          return response.json()
  try:
    df["instrument"] = np.where(df["base_currency"].isnull(),df["instrument"],df["base_currency"]+df["quote_currency"])
  except:
    try:  
        df["instrument"] = df["base_currency"]+df["quote_currency"]
    except:
        pass      

  #df["instrument"] = df["base_currency"]+df["quote_currency"]
  df["timestamp"] = response.json()["timestamp"]
  df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
  
  global _stats
  _stats = response.headers
  
  if fields == None:
      df = df[["instrument","timestamp","bid","mid","ask"]]
      return df
  else:
      column_list = column_list+fields 
      df = df[column_list]
      return df  

def historical(currency, date, fields=None, interval='daily'):
  if _api_key == None:
      return "please set your apikey using function set_rest_api_key"
  if type(fields) != type([]) and fields != None:
     return {"error":"fields must be a list, ex ['close']"}
  fx = currency.split(',')
  if interval.lower() == 'daily':
     freq = ''
     array = []
  else: 
    if interval == "hourly":
      interval = "hour"
    freq = interval+'_'
    array = []

  url = api_url+freq+'historical'
  if interval.lower() != 'daily':
    column_list = ["instrument","date_time"]
    for i in fx:
      querystring = {"currency":i,"date_time":date, "api_key":_api_key}
      response = requests.get(url, params=querystring)
      #print(response.json())
      array.append(response.json())
    try:
      df = pd.DataFrame(array)
    except:
        return response.json()
    try:
      df["instrument"] = np.where(df["currency"].isnull(),df["instrument"],df["currency"])
    except:
      try:  
          df["instrument"] = df["currency"]
      except:
          pass    
  else:
      column_list = ["instrument","date"]
      for n, i in enumerate(fx):
        if i.upper() in cfd_dict:
            fx[n] = i+"USD"
      currency = ",".join(fx)
      querystring = {"currency":currency,"date":date,"api_key":_api_key}
      response = requests.get(url, params=querystring)  
      # print(response.json())
      if "error" in response.json()["quotes"][0]:
        return response.json()["quotes"][0]
      df = pd.DataFrame.from_dict(response.json()["quotes"], orient='columns', dtype=None, columns=None)  
      
      df["date"] = response.json()["date"]
      df["date"] = pd.to_datetime(df["date"])
      inst_list = []
      for i in range(len(df)):
          newcur = df.iloc[i]["base_currency"]+df.iloc[i]["quote_currency"]
          
          if  newcur in cfd_crct:
              inst_list.append(cfd_crct[newcur]) 
          else:
              inst_list.append(newcur)
        
      df["instrument"] = inst_list      
      
  global _stats
  _stats = response.headers       
  if fields == None:
      column_list=column_list+["open","high","low","close"]
      df = df[column_list]
      return df
  else:
      column_list = column_list+fields 
      df = df[column_list]
      return df  

def timeseries(currency, start, end, fields=None, interval='daily', period=15):
  if _api_key == None:
      return "please set your apikey using function set_rest_api_key"
  fx = currency.split(',')
  if type(fields) != type([]) and fields != None:
     return {"error":"fields must be a list, ex ['close']"}
  else:
    if fields != ["close"] and len(fx) > 1:
      return {"error":"fields must be ['close'] when selecting multiple pairs"}
  array = []
  
  format = "split"
  dataframe = []
  url = api_url+"timeseries"

  if len(fx) > 1:
    dataframe = []
    #column_list = ["instrument","date_time"]
    for number, i in enumerate(fx):
        querystring = {"currency":i,"api_key":_api_key, "start_date":start,
                "interval":interval, "end_date":end, "period":period, "format":format}
        response = requests.get(url, params=querystring)  
        try:
          df = pd.DataFrame(response.json())
        except:
          return response.json()
        df = pd.DataFrame(df.quotes['data'], columns=df.quotes['columns'])  
        df = df.set_index('date')
        df = df.rename(columns={"close": i})
        if number == 0:
            hf = df[i]
        else:
            hf = pd.merge(hf,df[i], on="date",how='outer')      
    df = hf.reset_index()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
  else:
      #column_list = ["instrument","date"]
      querystring = {"currency":currency,"api_key":_api_key, "start_date":start,
                "interval":interval, "end_date":end, "period":period, "format":format}

      response = requests.get(url, params=querystring)  
      try:
          df = pd.DataFrame(response.json())
      except:
          return response.json()
      df = pd.DataFrame(df.quotes['data'], columns=df.quotes['columns'])

  global _stats
  _stats = response.headers       
  if fields == None:
      return df
  else:
      if len(fx) > 1:
        return df
      else:
        column_list = ["date"]+fields 
        df = df[column_list]
        return df  

