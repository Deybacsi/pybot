#!/usr/bin/python3




# éles key
#APIkey="kQKd4JP9IHAMdjo3Fhe26BCalFY3E8C8wDG5KisDODi2Y2Yo07nDS8wGHMRYjzAx"
#APIsecret="daUNlQ7ixUTyGNbFMFW9OurWRNKiD9cu0cUuF5OgXdlo8lcbVRawLehPW2WD4pXo"

#testnet key
# https://testnet.binance.vision/key/generate
#tAPIkey="DDRGTYu92D9SOHuzqMdsAqUuUgQchwoSxGtitjI85KptdJztdKZqJsnxfRCYmVgW"
#tAPIsecret="Q5YoQoSi5r6XJ6A0zp7bdnfzE51VVLnZg43NLf2pObJmYlPh9DVg14hk8VQX3o8y"

programname="2daMoonBot"
programversion="v0.1"

pybot_threads=[]
"""
pybot_threads.append({ 
    "threadname"    : "my BTC-USDT",    # to identify threads
    "asset1"        : "BTC",            # trading pairs
    "asset2"        : "USDT",
    "quantity"      : 15,              # used to buy asset1 with asset2 in specified amount (buy BTC for "quantity" USDT)
    "candlestobuy"  : 13,                # candles to wait until buy
    "candlestosell" : 13,                #                   and sell
    "stopped"       : False,            # can be used to temporary stop thread (also used to stop during runtime if balance insufficient)

    # used internally
    "asset1balance" : 0,                
    "asset2balance" : 0,
    "currentprice"  : 0
})
"""



from http import client
import os
import json
from multiprocessing import current_process
import time
import datetime
from datetime import timezone
from binance.client import Client
import curses               # windows: unicurses
from curses import wrapper

from matplotlib.pyplot import pause


actualthread=0

chartwindow={ "top" : 2,"left": 0, "width":0, "height":0}
statswindow={"top" : 2,"left": 0, "width":0,"height":0}
orderwindow={"top" : 2,"left": 0,"width":0,"height":0}

os.environ.setdefault('ESCDELAY', '25')     # set esc delay to 25ms

d=open('debug.log','w'); d.close()

def dl(str):
    d=open('debug.log','a')
    d.write(str+chr(13))
    d.close()
 
#json.dump(pybot_threads[0], open("pairs/myBTCUSDT.txt",'w'), indent=4)


#startup

settings=json.load(open("settings.txt"))

print(settings)



#reading pair configs
dir_list = os.listdir("pairs")
print("Reading pairs")
dl("Reading pairs")
dl(str(dir_list))
j=0
for i in range(0,len(dir_list)):
    if dir_list[i].find(".txt") > 0:
        print(' -',dir_list[i])
        pybot_threads.append(json.load(open("pairs/"+dir_list[i])))
        print(j)
        dl(dir_list[i]+' - '+str(pybot_threads[j]))
        pybot_threads[j]["threadname"]=dir_list[i].replace('.txt','')
        pybot_threads[j]["asset1balance"]=0
        pybot_threads[j]["asset2balance"]=0
        pybot_threads[j]["currentprice"]=0
        pybot_threads[j]["orders"]=[]
        j += 1
        
if len(pybot_threads)==0: print("No config files in 'pairs' directory. Nothing to read, please check documentation."); dl("No config files, exiting"); exit()
print()

# populate candles pricedata with 0
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


print("Connecting to Binance")
if settings["testmode"]: print("!!! TESTMODE !!!"); client = Client(settings["tapikey"], settings["tapisecret"], testnet=True)
else: client = Client(settings["apikey"], settings["apisecret"]); print("Connected")


# get current exchange balances for all threads
def getbalances():
    for actthread in range(0,len(pybot_threads)):
        pybot_threads[actthread]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset1"])["free"]
        pybot_threads[actthread]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset2"])["free"]

# get candle data for 1 thread
def getcandles(threadno):
    #pricedata=[]
    for i in range(0,len(pybot_threads)):   
        for j in range(0,500):
            pricedata[i][j]={
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
            }    
    print("Getting candledata for",pybot_threads[threadno]["asset1"]+pybot_threads[threadno]["asset2"],Client.KLINE_INTERVAL_15MINUTE+chr(13))
    candles = client.get_klines(symbol=pybot_threads[threadno]["asset1"]+pybot_threads[threadno]["asset2"], interval=Client.KLINE_INTERVAL_15MINUTE)
    print("Got",len(candles),"candles"+chr(13))
    print("Calculating moving averages and indicators"+chr(13))
    #populate pricedatas
    for i in range(0,len(candles)):

        pricedata[threadno][i]["ptime"] =int(candles[i][0]/1000)
        pricedata[threadno][i]["popen"] =float(candles[i][1])
        pricedata[threadno][i]["phigh"] =float(candles[i][2])
        pricedata[threadno][i]["plow"]  =float(candles[i][3])
        pricedata[threadno][i]["pclose"]=float(candles[i][4])
        # in testnet api there are huge high&low pikes
        if settings["testmode"]:
            #pricedata[threadno][i]["phigh"] =float(candles[i][1])
            #pricedata[threadno][i]["plow"]  =float(candles[i][1])
            if pricedata[threadno][i]["phigh"]>pricedata[threadno][i]["popen"]*1.01: pricedata[threadno][i]["phigh"]=pricedata[threadno][i]["popen"]*1.01
            if pricedata[threadno][i]["plow"]<pricedata[threadno][i]["popen"]*0.99: pricedata[threadno][i]["plow"]=pricedata[threadno][i]["popen"]*0.99

    # calc MAs
    print("MA7  ", sep='',end='')
    for i in range(7,len(candles)):
        if i % 10 == 0: print(".", sep='',end='')
        ma7sum=0
        for j in range(0,7):
            ma7sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma7"]=ma7sum/7
    print(""+chr(13))
    print("MA25 ", sep='',end='')
    for i in range(25,len(candles)):
        if i % 10 == 0: print(".", sep='',end='')
        ma25sum=0
        for j in range(0,25):
            ma25sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma25"]=ma25sum/25
    print(""+chr(13))
    print("MA99 ", sep='',end='')
    for i in range(99,len(candles)):
        if i % 10 == 0: print(".", sep='',end='')
        ma99sum=0
        for j in range(0,99):
            ma99sum+=pricedata[threadno][i-j]["popen"]
        pricedata[threadno][i]["ma99"]=ma99sum/99
    print(chr(13))
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
            +str(pricedata[threadno][i]["pclose"])+'|'
            +str(pricedata[threadno][i]["ma7"])+' '+str(pricedata[threadno][i]["ma25"])+' '+str(pricedata[threadno][i]["ma99"])+'|B:'+str(pricedata[threadno][i]["below"])+' A:'+str(pricedata[threadno][i]["above"])+chr(13))

    f.close()

#draw the price chart for 1 thread
def drawchart(threadno,stdscr):

    def calcy(theprice):
        chartwindowheight=chartwindow["top"]+chartwindow["height"]
        they=chartwindowheight-int((theprice-pricemin)/charheightprice+0.5)
        if they<chartwindow["top"]: they=0                                                                       # overwritten by header row
        if they>chartwindow["top"]+chartwindow["height"]: they=chartwindow["top"]+chartwindow["height"]+2     # overwritten by ^ - v row
        return they

    pricemin=pricedata[threadno][len(pricedata[threadno])-1]["popen"]
    pricemax=pricedata[threadno][len(pricedata[threadno])-1]["popen"]
    for i in range(0,chartwindow["width"]):
        if pricedata[threadno][len(pricedata[threadno])-1-i]["plow"]  <pricemin: pricemin=pricedata[threadno][len(pricedata[threadno])-1-i]["plow"]
        if pricedata[threadno][len(pricedata[threadno])-1-i]["phigh"] >pricemax: pricemax=pricedata[threadno][len(pricedata[threadno])-1-i]["phigh"]

    #horizontal lines
    for i in range(1,5):
        for j in range(0,chartwindow["width"],5):
            stdscr.addstr(chartwindow["top"]+int(chartwindow["height"]/5*i),j,"-")
        stdscr.addstr(chartwindow["top"]+int(chartwindow["height"]/5*i),0,str(round(pricemax-(pricemax-pricemin)/5*i,2)),curses.A_DIM)
    
    charheightprice=(pricemax-pricemin)/chartwindow["height"]
    
    for i in range(0,chartwindow["width"]+1):
        actprice=pricedata[threadno][len(pricedata[threadno])-1-i]
        chartwindowheight=chartwindow["top"]+chartwindow["height"]
        chartwindowwidth =chartwindow["left"]+chartwindow["width"]
        # candle kanóc
        for j in range(calcy(actprice["phigh"]), calcy(actprice["plow"])+1):
            stdscr.addstr(j,chartwindowwidth-i,"|")                    

        # MAs
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

        # write out min/max prices
        if actprice["phigh"]==pricemax:
            stdscr.addstr(chartwindow["top"]-1,chartwindowwidth-i,str(pricemax))
        if actprice["plow"]==pricemin:
            stdscr.addstr(chartwindowheight+1,chartwindowwidth-i,str(pricemin))

        # ^ and v indicators
        if actprice["above"]:
            stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,'^',curses.color_pair(3))
        else:
            if actprice["below"]:
                stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,'v',curses.color_pair(2))     
            else:
                stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,'-')       

# draw the whole screen
def drawwindow(stdscr):
    # if window too small
    if curses.COLS<80 or curses.LINES<33:
        stdscr.clear(); stdscr.addstr(12,2,"Increase window size :) "); return
 
    chartwindow["width"]=curses.COLS -1 - chartwindow["left"] 
    chartwindow["height"]=int(curses.LINES/2)
    statswindow["top"]=chartwindow["top"]+chartwindow["height"]+3
    statswindow["width"]=chartwindow["width"]
    statswindow["height"]=5
    orderwindow["top"]=statswindow["top"]+statswindow["height"]+1
    orderwindow["left"]=int(curses.COLS/2)
    orderwindow["width"]=chartwindow["width"]
    orderwindow["height"]=curses.LINES-orderwindow["top"]-1    
    stdscr.clear()
    drawchart(actualthread,stdscr)
    for i in range(0,curses.COLS):
        stdscr.addstr(0,i," ",curses.color_pair(1))
    stdscr.addstr(0,1,'Thread '+str(actualthread)+' | '+pybot_threads[actualthread]["threadname"]+' | Pair: '+pybot_threads[actualthread]["asset1"]+'/'+pybot_threads[actualthread]["asset2"],curses.color_pair(1))
    stdscr.addstr(0,curses.COLS-12,"Refresh: ",curses.color_pair(1))
    stdscr.addstr(statswindow["top"],statswindow["left"]+1,'Price: '+str(pybot_threads[actualthread]["currentprice"])+' '+pybot_threads[actualthread]["asset2"],curses.A_BOLD)

    stdscr.addstr(statswindow["top"]+1,statswindow["left"]+1,'Balances:')
    stdscr.addstr(statswindow["top"]+2,statswindow["left"]+1,pybot_threads[actualthread]["asset1"]+':')
    stdscr.addstr(statswindow["top"]+2,statswindow["left"]+1+7,str(pybot_threads[actualthread]["asset1balance"]))
    stdscr.addstr(statswindow["top"]+3,statswindow["left"]+1,pybot_threads[actualthread]["asset2"]+':')
    stdscr.addstr(statswindow["top"]+3,statswindow["left"]+1+7,str(pybot_threads[actualthread]["asset2balance"]))

    stdscr.addstr(statswindow["top"]  ,chartwindow["left"]+chartwindow["width"]-pybot_threads[actualthread]["candlestosell"]+1-17,"Candles to sell |")
    stdscr.addstr(statswindow["top"]+1,chartwindow["left"]+chartwindow["width"]-pybot_threads[actualthread]["candlestobuy"] +1-16,"Candles to buy |")

    # draw S and B indicators
    # SELL
    for i in range(0,pybot_threads[actualthread]["candlestosell"]):
        if pricedata[actualthread][len(pricedata[actualthread])-1-i]["above"]==True:
            stdscr.addstr(statswindow["top"],chartwindow["left"]+chartwindow["width"]-i,"S",curses.color_pair(3))
        else:
            stdscr.addstr(statswindow["top"],chartwindow["left"]+chartwindow["width"]-i,"-",curses.A_DIM)
    # BUY
    for i in range(0,pybot_threads[actualthread]["candlestobuy"]):
        if pricedata[actualthread][len(pricedata[actualthread])-1-i]["below"]==True:
            stdscr.addstr(statswindow["top"]+1,chartwindow["left"]+chartwindow["width"]-i,"B",curses.color_pair(2))
        else:
            stdscr.addstr(statswindow["top"]+1,chartwindow["left"]+chartwindow["width"]-i,"-",curses.A_DIM)

    # order list
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+7 ,pybot_threads[actualthread]["asset1"])
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+16,pybot_threads[actualthread]["asset2"])
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+26,"P/L")
    for i in range(0,orderwindow["height"]):
        stdscr.addstr(orderwindow["top"]+1+i,orderwindow["left"],'|')
        
        if len(pybot_threads[actualthread]["orders"])-1-i>=0:
            actorder=pybot_threads[actualthread]["orders"][len(pybot_threads[actualthread]["orders"])-1-i]
            ordercolor=curses.color_pair(0)
            if actorder["side"]=="SELL":
                profitloss=round((float(actorder["cummulativeQuoteQty"])/float(pybot_threads[actualthread]["orders"][len(pybot_threads[actualthread]["orders"])-1-i-1]["cummulativeQuoteQty"])-1)*100,2)
                if profitloss>=0: ordercolor=curses.color_pair(3)
                else: ordercolor=curses.color_pair(2)
                stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+30-len(str(profitloss)),str(profitloss)+'%',ordercolor)

            #dl(str(actorder))
            # buy/sell
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+2,actorder["side"],ordercolor)
            # date
            trtime=str(datetime.datetime.fromtimestamp(int(actorder["transactTime"]/1000), tz=timezone.utc ))
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7   ,trtime[:-9],ordercolor)
            # asset1
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+14
                -len(actorder["executedQty"]), actorder["executedQty"],ordercolor)             
            # asset2
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+14+8
                -len(str(round(float(actorder["cummulativeQuoteQty"]),2))), str(round(float(actorder["cummulativeQuoteQty"]),2)),ordercolor)
            
           
    


def loadorders(threadno):
    pybot_threads[threadno]["orders"]=[]
    if settings["testmode"]: tfilename="-test"
    else: tfilename=""
    fo=open("pairs/"+pybot_threads[threadno]["threadname"]+tfilename+".trades",'r')
    fstr=''
    for fline in fo:
        
        if fline.find('-#-#-#-#-')==-1:
            fstr +=  fline
        else: 
            pybot_threads[threadno]["orders"].append(json.loads(fstr));
            #dl(fstr)
            #dl('-------------------------------------------------------------------------------------------')
            fstr=''
        
def saveorder(threadno,order):
    if settings["testmode"]: tfilename="-test"
    else: tfilename=""
    json.dump(order, open("pairs/"+pybot_threads[threadno]["threadname"]+tfilename+".trades",'a'), indent=4)
    fo=open("pairs/"+pybot_threads[threadno]["threadname"]+tfilename+".trades",'a')
    fo.write(chr(10)+'-#-#-#-#-'+chr(10))
    fo.close


refreshtime=60
elapsed = 0

# main prog
def main(stdscr):
    pressedkey=0

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
    stdscr.nodelay(1)
    while True:


        stdscr.clear()
        stdscr.refresh()
        getbalances()
        print("Getting balances and symbol info"+chr(13))
        for i in range(0,len(pybot_threads)):
            print(pybot_threads[i]["asset1"],':',pybot_threads[i]["asset1balance"]+chr(13))
            print(pybot_threads[i]["asset2"],':',pybot_threads[i]["asset2balance"]+chr(13))
            pybot_threads[i]["symbol_info"]=client.get_symbol_info(pybot_threads[i]["asset1"]+pybot_threads[i]["asset2"])
            print(pybot_threads[i]["symbol_info"]["symbol"]+' Status: '+pybot_threads[i]["symbol_info"]["status"]+' SpotAllowed: '+str(pybot_threads[i]["symbol_info"]["isSpotTradingAllowed"])+chr(13))
            dl(str(pybot_threads[i]["symbol_info"]))

        for actthread in range(0,len(pybot_threads)):
            getcandles(actthread)
            print("Get current price")
            pybot_threads[actthread]["currentprice"] = float(client.get_avg_price(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])["price"])
            dl(str(pybot_threads[actthread]["currentprice"]))

            oktobuycounter=0
            oktosellcounter=0
            dl(str(pricedata))
            # count prev candles if below
            for i in range(len(pricedata[actthread])-1,
                    len(pricedata[actthread])-1-pybot_threads[actthread]["candlestobuy"],-1):
                if pricedata[actthread][i]["below"]==True:
                    oktobuycounter += 1
            # check current price if below
            if  (pybot_threads[actthread]["currentprice"]<pricedata[actthread][len(pricedata[actthread])-1]["ma7"] and
                pybot_threads[actthread]["currentprice"]<pricedata[actthread][len(pricedata[actthread])-1]["ma25"] and
                pybot_threads[actthread]["currentprice"]<pricedata[actthread][len(pricedata[actthread])-1]["ma99"]):
                    oktobuycounter += 1
            # prev candles  if above
            for i in range(len(pricedata[actthread])-1,len(pricedata[actthread])-1-pybot_threads[actthread]["candlestosell"],-1):                
                if pricedata[actthread][i]["above"]==True:
                    oktosellcounter += 1
            #check current price if above
            if  (pybot_threads[actthread]["currentprice"]>pricedata[actthread][len(pricedata[actthread])-1]["ma7"] and
                pybot_threads[actthread]["currentprice"]>pricedata[actthread][len(pricedata[actthread])-1]["ma25"] and
                pybot_threads[actthread]["currentprice"]>pricedata[actthread][len(pricedata[actthread])-1]["ma99"]):
                    oktosellcounter += 1                
            loadorders(actthread)

            lastorder=""
            if len(pybot_threads[actthread]["orders"])==0:      # if there are no orders, we will start with a buy next
                lastorder="SELL"
            if len(pybot_threads[actthread]["orders"])>0:
                lastorder=pybot_threads[actthread]["orders"][len(pybot_threads[actthread]["orders"])-1]

            # buy order
            dl(str(oktobuycounter))
            dl(str(oktosellcounter))
            dl(str(lastorder))
            if oktobuycounter==pybot_threads[actthread]["candlestobuy"]+1 and lastorder["side"]=="SELL":
                saveorder(actthread,client.order_market_buy(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"], quoteOrderQty=pybot_threads[actthread]["quantity"]))
                pass


            # TODO

            # SZÁZALÉKOT BELE!
            # sell order
            if oktosellcounter==pybot_threads[actthread]["candlestosell"]+1 and lastorder["side"]=="BUY":
                saveorder(actthread,client.order_market_sell(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"], quantity=lastorder["executedQty"]))
                pass

                    


            # UTC!  
            #saveorder(0,client.order_market_buy(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"], quantity=lastorder["lastorder"]))
            

            """

            {
                "symbol": "BTCUSDT",
                "orderId": 5585808,
                "orderListId": -1,
                "clientOrderId": "nPymTDDI2pjH0yMbVFyarL",
                "transactTime": 1665940755075,
                "price": "0.00000000",
                "origQty": "0.00052200",
                "executedQty": "0.00052200", - ez a vett db
                "cummulativeQuoteQty": "9.99351774",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "BUY",
                "fills": [
                    {
                        "price": "19144.67000000",
                        "qty": "0.00052200",
                        "commission": "0.00000000",
                        "commissionAsset": "BTC",
                        "tradeId": 2046567
                    }
                ]
            }
            """

        #drawwindow(stdscr)
        start = time.time()
        elapsed=0
        while elapsed < refreshtime:
            elapsed = int(time.time() - start)
            drawwindow(stdscr)
            stdscr.addstr(0,curses.COLS-3,"   ",curses.color_pair(1))
            stdscr.addstr(0,curses.COLS-3,str(60-elapsed),curses.color_pair(1))
            stdscr.refresh()
            time.sleep(0.25) 


            pressedkey=stdscr.getch()
            if pressedkey==27:
                curses.endwin(); print();print(); print("Thanks for using",programname,programversion); print(); exit()
            if pressedkey==curses.KEY_RESIZE:
                curses.LINES, curses.COLS = stdscr.getmaxyx()








    
    
    



    #if 
    #order = client.order_market_buy(
    #    symbol=pybot_threads[actualthread]["asset1"]+pybot_threads[actualthread]["asset2"],
    #    quantity=pybot_threads[actualthread]["quantity"]
    #)

    #currenttime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(candles[len(candles)-1][0]/1000))
    #utctime=datetime.datetime.fromtimestamp(candles[len(candles)-1][0]/1000, tz=timezone.utc)

    #currentprice=float(client.get_avg_price(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])["price"])
    #print(utctime,' - (', currenttime,' local)')
    #print('MA 7,25,99: ',ma7, ma25, ma99)
    #print('Price     : ',currentprice)


    

print("Initializing screen")
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

fold All folds all regions in the editor:
Ctrl + K, Ctrl + 0 (zero) on Windows and Linux

Unfold All unfolds all regions in the editor:
Ctrl + K, Ctrl + J on Windows and Linux


eazybot:
https://www.youtube.com/watch?v=3ztxbDP5fNc&t=12s
"""


