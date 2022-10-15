#!/usr/bin/python3

#TESTMODE=True
TESTMODE=False

# éles key
APIkey="kQKd4JP9IHAMdjo3Fhe26BCalFY3E8C8wDG5KisDODi2Y2Yo07nDS8wGHMRYjzAx"
APIsecret="daUNlQ7ixUTyGNbFMFW9OurWRNKiD9cu0cUuF5OgXdlo8lcbVRawLehPW2WD4pXo"

#testnet key
# https://testnet.binance.vision/key/generate
tAPIkey="DDRGTYu92D9SOHuzqMdsAqUuUgQchwoSxGtitjI85KptdJztdKZqJsnxfRCYmVgW"
tAPIsecret="Q5YoQoSi5r6XJ6A0zp7bdnfzE51VVLnZg43NLf2pObJmYlPh9DVg14hk8VQX3o8y"


pybot_threads=[]
pybot_threads.append({ 
    "threadname"    : "my BTC-USDT",    # to identify threads
    "asset1"        : "BTC",            # trading pairs
    "asset2"        : "USDT",
    "amount"        : 100,              # used to buy asset1 with asset2 in specified amount (buy x BTC for 100USDT)
    "candlestobuy"  : 3,                # candles to wait until buy
    "candlestosell" : 3,                #                   and sell
    "stopped"       : False,            # can be used to temporary stop thread (also used to stop during runtime if balance insufficient)

    # used internally
    "asset1balance" : 0,                
    "asset2balance" : 0
})



# -------- Don't edit below this line -----------

import json
import time
import datetime
from datetime import timezone
from binance.client import Client
import curses               # windows: unicurses
from curses import wrapper

import checks


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







print("Connecting to Binance")
if TESTMODE:
    print("TESTMODE ON")
    client = Client(tAPIkey, tAPIsecret, testnet=True)
else:
    client = Client(APIkey, APIsecret)
print("ok")

#info = client.get_symbol_info('BTCUSDT')

for actthread in range(0,len(pybot_threads)):

    pybot_threads[actthread]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset1"])["free"]
    pybot_threads[actthread]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset2"])["free"]

    print(pybot_threads[actthread]["asset1"],'balance:',pybot_threads[actthread]["asset1balance"])
    print(pybot_threads[actthread]["asset2"],'balance:',pybot_threads[actthread]["asset2balance"])


d=open('debug.log','w')
d.close()

def dl(str):
    d=open('debug.log','a')
    d.write(str+chr(13))
    d.close()
 


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
        if pricedata[threadno][i]["phigh"]==90000.4: pricedata[threadno][i]["phigh"]=19200.58
        if pricedata[threadno][i]["phigh"]==45500: pricedata[threadno][i]["phigh"]=19200.58


        
    # calc MAs
    for i in range(7,len(candles)):
        ma7sum=0
        for j in range(0,7):
            ma7sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma7"]=ma7sum/7
    for i in range(25,len(candles)):
        ma25sum=0
        for j in range(0,25):
            ma25sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma25"]=ma25sum/25
    for i in range(99,len(candles)):
        ma99sum=0
        for j in range(0,99):
            ma99sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma99"]=ma99sum/99

    # calc above&below indicators    
    for i in range(0,len(candles)):
        if pricedata[threadno][i]["popen"]<pricedata[threadno][i]["ma7"] and pricedata[threadno][i]["popen"]<pricedata[threadno][i]["ma25"] and pricedata[threadno][i]["popen"]<pricedata[threadno][i]["ma99"]:
            pricedata[threadno][i]["below"]=True
        if pricedata[threadno][i]["popen"]>pricedata[threadno][i]["ma7"] and pricedata[threadno][i]["popen"]>pricedata[threadno][i]["ma25"] and pricedata[threadno][i]["popen"]>pricedata[threadno][i]["ma99"]:
            pricedata[threadno][i]["above"]=True
                
        #print(i,pricedata[threadno][i]["popen"], pricedata[threadno][i]["ma7"],pricedata[threadno][i]["ma25"],pricedata[threadno][i]["ma99"],pricedata[threadno][i]["below"],pricedata[threadno][i]["above"])
    f=open('candledata.log','w')
    for i in range(0,len(candles)):
        
        f.write(str(i)+' '+str(pricedata[threadno][i]["popen"])+' '
            +str(pricedata[threadno][i]["phigh"])+' '
            +str(pricedata[threadno][i]["plow"])+' '
            +str(pricedata[threadno][i]["pclose"])+' '
            +str(pricedata[threadno][i]["ma7"])+' '+str(pricedata[threadno][i]["ma25"])+' '+str(pricedata[threadno][i]["ma99"])+' '+str(pricedata[threadno][i]["below"])+' '+str(pricedata[threadno][i]["above"])+chr(13))

    f.close()


actualthread=0

chartwindow={
    "top" : 2,
    "left": 0,
    "width":0,
    "height":0
}

def drawchart(threadno,stdscr):

    def calcy(theprice):
        chartwindowheight=chartwindow["top"]+chartwindow["height"]
        chartwindowwidth =chartwindow["left"]+chartwindow["width"]
        they=chartwindowheight-int((theprice-pricemin)/charheightprice+0.5)
        if they<chartwindow["top"]: they=0                                                                       # overwritten by header row
        if they>chartwindow["top"]+chartwindow["height"]-1: they=chartwindow["top"]+chartwindow["height"]+2     # overwritten by ^ - v row
        return they




    pricemin=pricedata[threadno][len(pricedata[threadno])-1]["popen"]
    pricemax=pricedata[threadno][len(pricedata[threadno])-1]["popen"]
    for i in range(0,chartwindow["width"]):
        if pricedata[threadno][len(pricedata[threadno])-1-i]["plow"]  <pricemin: pricemin=pricedata[threadno][len(pricedata[threadno])-1-i]["plow"]
        if pricedata[threadno][len(pricedata[threadno])-1-i]["phigh"] >pricemax: pricemax=pricedata[threadno][len(pricedata[threadno])-1-i]["phigh"]

        dl(str(len(pricedata[threadno])-1-i)+' '+str(pricedata[threadno][len(pricedata)-1-i])+' '+str(pricemin)+' '+str(pricemax))

    #horizontal lines
    for i in range(1,5):
        for j in range(0,chartwindow["width"],5):
            stdscr.addstr(chartwindow["top"]+int(chartwindow["height"]/5*i),j,"-")
        stdscr.addstr(chartwindow["top"]+int(chartwindow["height"]/5*i),0,str(round(pricemax-(pricemax-pricemin)/5*i,2)))
    
    charheightprice=(pricemax-pricemin)/chartwindow["height"]
    
    for i in range(0,chartwindow["width"]):
        actprice=pricedata[threadno][len(pricedata[threadno])-1-i]
        chartwindowheight=chartwindow["top"]+chartwindow["height"]
        chartwindowwidth =chartwindow["left"]+chartwindow["width"]
        # candle kanóc
        #for j in range(chartwindowheight-int((actprice["phigh"]-pricemin)/charheightprice+0.5),
        #               chartwindowheight-int((actprice["plow"]-pricemin)/charheightprice+0.5)+1):
        #    stdscr.addstr(j,chartwindowwidth-i,"|")
        for j in range(calcy(actprice["phigh"]), calcy(actprice["plow"])+1):
            stdscr.addstr(j,chartwindowwidth-i,"|")                    

        dl(str(chartwindowheight-int((actprice["ma99"]-pricemin)/charheightprice+0.5)))

        stdscr.addstr(calcy(actprice["ma99"]),chartwindowwidth-i,"˙",curses.color_pair(9))
        stdscr.addstr(calcy(actprice["ma25"]),chartwindowwidth-i,"˙",curses.color_pair(8))
        stdscr.addstr(calcy(actprice["ma7"]),chartwindowwidth-i,"˙",curses.color_pair(7))

        # candle body
        # red
        if actprice["popen"]>actprice["pclose"]:    
            for j in range( calcy(actprice["popen"]), calcy(actprice["pclose"])+1): 
                stdscr.addstr(j,chartwindowwidth-i,"X",curses.color_pair(5))
        else:
            # green
            for j in range( calcy(actprice["pclose"]), calcy(actprice["popen"])+1): 
                stdscr.addstr(j,chartwindowwidth-i,"X",curses.color_pair(6))
        if actprice["phigh"]==pricemax:
            stdscr.addstr(chartwindow["top"]-1,chartwindowwidth-i,str(pricemax))
        if actprice["plow"]==pricemin:
            stdscr.addstr(chartwindowheight+1,chartwindowwidth-i,str(pricemin))

        if actprice["above"]:
            stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,'^',curses.color_pair(3))
        else:
            if actprice["below"]:
                stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,'v',curses.color_pair(2))     
            else:
                stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,'-')       


def drawwindow(stdscr):
    stdscr.clear()
    drawchart(actualthread,stdscr)
    for i in range(0,curses.COLS):
        stdscr.addstr(0,i," ",curses.color_pair(1))
    stdscr.addstr(0,1,str(actualthread)+' '+pybot_threads[actualthread]["threadname"]+'-'+pybot_threads[actualthread]["asset1"]+'/'+pybot_threads[actualthread]["asset2"],curses.color_pair(1))






def main(stdscr):
    # Clear screen
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_GREEN)
    
    # MAs
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.curs_set(False)
    stdscr.clear()
    chartwindow["width"]=curses.COLS -1 - chartwindow["left"] 
    chartwindow["height"]=int(curses.LINES/3)

    

    getcandles(0)
    drawwindow(stdscr)

    stdscr.addstr(chartwindow["top"]+chartwindow["height"]+1,0,"alja")

    #currenttime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(candles[len(candles)-1][0]/1000))
    #utctime=datetime.datetime.fromtimestamp(candles[len(candles)-1][0]/1000, tz=timezone.utc)

    #currentprice=float(client.get_avg_price(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])["price"])
    #print(utctime,' - (', currenttime,' local)')
    #print('MA 7,25,99: ',ma7, ma25, ma99)
    #print('Price     : ',currentprice)

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)



"""

(0,0) to (curses.LINES - 1, curses.COLS - 1).


https://binance-docs.github.io/apidocs/spot/en/#introduction
https://testnet.binance.vision/



pip install python-binance

https://python-binance.readthedocs.io/en/latest/market_data.html


curses:
https://docs.python.org/3/howto/curses.html

https://docs.python.org/3/library/curses.html#module-curses

"""


