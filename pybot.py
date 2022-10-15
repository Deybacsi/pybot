#!/usr/bin/python3
import json
import time
import datetime
from datetime import timezone
from binance.client import Client
import curses               # windows: unicurses
from curses import wrapper

import checks



pybot_threads=[]
pybot_threads.append({
    
        #"pair"  : "BTCUSDT",
        "threadname"    : "my BTC-USDT",    # to identify threads
        "asset1"        : "BTC",            # trading pairs
        "asset2"        : "USDT",
        "amount"        : 100,              # used to buy asset1 with asset2 in specified amount
        "candlestobuy"  : 3,                # candles to wait until buy
        "candlestosell" : 3,                #                   and sell
        "stopped"       : False,            # can be used to temporary stop thread (also used to stop during runtime if balance insufficient)

        # used internally
        "asset1balance" : 0,                
        "asset2balance" : 0

})


pricedata=[]
for i in range(0,len(pybot_threads)):
    pricedata.append([])
    for j in range(0,500):
        pricedata[i].append({
            "ptime" : 0,
            "popen" : 0,
            "phigh" : 0,
            "plow"  : 0,
            "pclose": 0,
            "ma7"   : 0,
            "ma25"  : 0,
            "ma99"  : 0,
            "below" : False,
            "above" : False
        })


print (len(pybot_threads))
print(pybot_threads)




# éles key
#APIkey="kQKd4JP9IHAMdjo3Fhe26BCalFY3E8C8wDG5KisDODi2Y2Yo07nDS8wGHMRYjzAx"
#APIsecret="daUNlQ7ixUTyGNbFMFW9OurWRNKiD9cu0cUuF5OgXdlo8lcbVRawLehPW2WD4pXo"

#testnet key
# https://testnet.binance.vision/key/generate
tAPIkey="DDRGTYu92D9SOHuzqMdsAqUuUgQchwoSxGtitjI85KptdJztdKZqJsnxfRCYmVgW"
tAPIsecret="Q5YoQoSi5r6XJ6A0zp7bdnfzE51VVLnZg43NLf2pObJmYlPh9DVg14hk8VQX3o8y"



print("connect to testnet")
client = Client(tAPIkey, tAPIsecret, testnet=True)
print("ok")

#info = client.get_symbol_info('BTCUSDT')

for actthread in range(0,len(pybot_threads)):
    blaance=0
    pybot_threads[actthread]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset1"])["free"]
    pybot_threads[actthread]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset2"])["free"]

    print(pybot_threads[actthread]["asset1"],'balance:',pybot_threads[actthread]["asset1balance"])
    print(pybot_threads[actthread]["asset2"],'balance:',pybot_threads[actthread]["asset2balance"])



    tobuy=False
    belowmacounter=0
    #for i in range(len(candles)-1,len(candles)-pybot_threads[actthread]["candlestobuy"]-1):
        #if candles[i][4]<


# get candle data for thread
def getcandles(threadno):
    candles = client.get_klines(symbol=pybot_threads[threadno]["asset1"]+pybot_threads[threadno]["asset2"], interval=Client.KLINE_INTERVAL_15MINUTE)
    #populate pricedatas
    for i in range(0,len(candles)):
        pricedata[threadno][i]["ptime"] =int(candles[i][0]/1000)
        pricedata[threadno][i]["popen"] =float(candles[i][1])
        pricedata[threadno][i]["phigh"] =float(candles[i][2])
        pricedata[threadno][i]["plow"]  =float(candles[i][3])
        pricedata[threadno][i]["pclose"]=float(candles[i][4])
        
    # calc MAs
    for i in range(7,len(candles)):
        ma7sum=0
        for j in range(0,7):
            ma7sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma7"]=round(ma7sum/7,2)
    for i in range(25,len(candles)):
        ma25sum=0
        for j in range(0,25):
            ma25sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma25"]=round(ma25sum/25,2)
    for i in range(99,len(candles)):
        ma99sum=0
        for j in range(0,99):
            ma99sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma99"]=round(ma99sum/99,2)
        
    # calc above&below indicators    
    for i in range(0,len(candles)):
        if pricedata[threadno][i]["popen"]<pricedata[threadno][i]["ma7"] and pricedata[threadno][i]["popen"]<pricedata[threadno][i]["ma25"] and pricedata[threadno][i]["popen"]<pricedata[threadno][i]["ma99"]:
            pricedata[threadno][i]["below"]=True
        if pricedata[threadno][i]["popen"]>pricedata[threadno][i]["ma7"] and pricedata[threadno][i]["popen"]>pricedata[threadno][i]["ma25"] and pricedata[threadno][i]["popen"]>pricedata[threadno][i]["ma99"]:
            pricedata[threadno][i]["above"]=True
                
        print(i,pricedata[threadno][i]["popen"], pricedata[threadno][i]["ma7"],pricedata[threadno][i]["ma25"],pricedata[threadno][i]["ma99"],pricedata[threadno][i]["below"],pricedata[threadno][i]["above"])


    #print(candles)
    #print(len(candles))

    for i in range(len(candles)-1,len(candles)-8,-1):
        
        ma7sum += float(candles[i][4])
        #print(i, candles[i][1], ma7sum)
    

    ma25=0
    ma25sum=0
    for i in range(len(candles)-1,len(candles)-26,-1):
        
        ma25sum += float(candles[i][4])
        #print(i, candles[i][1], ma25sum)
    ma25=ma25sum/25

    ma99=0
    ma99sum=0
    for i in range(len(candles)-1,len(candles)-100,-1):
        
        ma99sum += float(candles[i][4])
        #print(i, candles[i][1], ma99sum)
    ma99=ma99sum/99



#def main(stdscr):
    # Clear screen
    #stdscr.clear()

getcandles(0)

#currenttime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(candles[len(candles)-1][0]/1000))
#utctime=datetime.datetime.fromtimestamp(candles[len(candles)-1][0]/1000, tz=timezone.utc)

#currentprice=float(client.get_avg_price(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])["price"])
print(utctime,' - (', currenttime,' local)')
print('MA 7,25,99: ',ma7, ma25, ma99)
print('Price     : ',currentprice)

    #stdscr.refresh()
    #stdscr.getkey()

#wrapper(main)



"""
https://towardsdatascience.com/plotly-dashboards-in-python-28a3bb83702c
https://towardsdatascience.com/how-to-create-stunning-web-apps-for-your-data-science-projects-c7791102134e

https://binance-docs.github.io/apidocs/spot/en/#introduction
https://testnet.binance.vision/



pip install python-binance

https://python-binance.readthedocs.io/en/latest/market_data.html


curses:
https://docs.python.org/3/howto/curses.html


"""


