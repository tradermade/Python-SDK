TraderMade SDK
==============

tradermade is Python SDK for getting forex data via REST API or
Websocket.

Installation
------------

Use the package manager `pip`_ to install foobar.

.. code:: bash

   pip install tradermade

Get API key by signing up for `free`_

Usage
-----

REST API
~~~~~~~~

.. code:: python

   import tradermade as tm

   # set api key
   tm.set_rest_api_key(api_key)


   tm.live(currency='EURUSD,GBPUSD',fields=["bid", "mid", "ask"]) # returns live data - fields is optional
    
   tm.historical(currency='EURUSD,GBPUSD', date="2021-04-22",interval="daily", fields=["open", "high", "low","close"]) # returns historical data for the currency requested interval is daily, hourly, minute - fields is optional

   tm.timeseries(currency='EURUSD', start="2021-04-20",end="2021-04-22",interval="hourly",fields=["open", "high", "low","close"]) # returns timeseries data for the currency requested interval is daily, hourly, minute - fields is optional

   tm.cfd_list() # gets a list of all cfds available

   tm.currency_list() # gets a list of all currency codes available add two codes to get code for currency pair ex EUR + USD gets EURUSD

Streaming Data
~~~~~~~~~~~~~~

.. code:: python

   from tradermade import stream

   def print_message(data):
      print(f"Received: {data}")

   api_key = "api_key"

    # set streaming key - not the same as rest API key
   stream.set_ws_key(api_key)

   stream.set_symbols("USDJPY,EURGBP")
   
   # Set the callback for receiving messages
   stream.stream_data(print_message)  

   stream.connect()

Contributing
------------

For changes, please open an issue to discuss what you would like to
change.

License
-------

`MIT`_

.. _pip: https://pip.pypa.io/en/stable/
.. _free: https://marketdata.tradermade.com/signup
.. _MIT: https://choosealicense.com/licenses/mit/
