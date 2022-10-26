#!/usr/bin/python3

programname="2daMoonBot"
programversion="v0.1.05"

print(programname, programversion)

#from http import client
#from multiprocessing import current_process

import os
import json
import time
import datetime
from datetime import timezone
import urllib.request
import curses               # windows: windows-curses
from curses import wrapper
print("Starting Binance module")
from binance.client import Client

# thread's data
pybot_threads=[]
# thread displayed on screen
actualthread=0

# seconds between refreshes
# in every refresh, bot calculates data, and checks for buy/sell indicators
# if they signals, bot will buy/sell
refreshtime=60
# counter for elapsed time in seconds
elapsed = 0

# shitty subwindows defs, values recalculated in drawwindow
chartwindow={"top" : 3,"left": 1, "width":0, "height":0}
statswindow={"top" : 2,"left": 1, "width":0,"height":0}
orderwindow={"top" : 2,"left": 1,"width":0,"height":0}
leftwindow ={"top" : 2,"left": 1,"width":0,"height":0}

U_CANDLEBODY = "▉"
U_CANDLEWICK = "│"
U_MACHARTUP  = "⋰"
U_MACHARTDOWN= "⋱"
U_MACHART    = "⋯"
U_CHECKMARK  = "✔️"
U_ARROWUP    = "↑"
U_ARROWDOWN  = "↓"
U_BULLET     = "•"

U_BOX_HORZ  = "─"
U_BOX_VERT  = "│"
U_BOX_VERTH = "╵"


U_BOX_HORZDOT= "┈"

U_BOX_TOPLEFT   = "┌"
U_BOX_TOPRIGHT  = "┐" 
U_BOX_BOTLEFT   = "└"
U_BOX_BOTRIGHT  = "┘"
U_BOX_CROSS     = "┼"
U_BOX_TUP       = "┬"
U_BOX_TDOWN     = "┴"
U_BOX_TLEFT     = "├"
U_BOX_TRIGHT    = "┤"


os.environ.setdefault('ESCDELAY', '25')     # set esc key delay to 25ms

print("Searching for updates")
print("---------------------")
for line in urllib.request.urlopen("https://raw.githubusercontent.com/Deybacsi/pybot/main/version.no"):
    remoteversion=line.decode('utf-8')
    print("Your version:",programversion)
    print("New  version:",remoteversion)          
    if programversion<remoteversion:
        print("-------------------------------------------------")
        print("You are using an outdated version, please update!")
        print("-------------------------------------------------")

        print("Download from: https://github.com/Deybacsi/pybot")
        print("(git pull?)")
        exit()
        
v=open('version.no','w'); v.write(programversion); v.close()

# init debug log, and dl()
d=open('log/debug.log','w'); d.close()
def dl(str):
    d=open('log/debug.log','a')
    d.write(str+chr(13))
    d.close()

# temporary candledata, only for debug
fcd=open('log/candledata.log','w'); fcd.close()

# checking settings.txt
try:
    settings=json.load(open("settings.txt"))
except FileNotFoundError:
    print('No settings.txt!\nRename default_settings.txt and fill in API keys data!')
    exit(1)

#print(settings)


#reading pair config files
dir_list = sorted(os.listdir("pairs"))
print("Reading pairs")
dl("Reading pairs")
dl(str(dir_list))
j=0
for i in range(0,len(dir_list)):
    if dir_list[i].find(".txt") > 0:
        print(j,'-',dir_list[i])
        pybot_threads.append(json.load(open("pairs/"+dir_list[i])))
        dl(dir_list[i]+' - '+str(pybot_threads[j]))
        pybot_threads[j]["threadname"]=dir_list[i].replace('.txt','')
        pybot_threads[j]["asset1balance"]=0
        pybot_threads[j]["asset2balance"]=0
        pybot_threads[j]["currentprice"]=0
        pybot_threads[j]["orders"]=[]
        j += 1
        
if len(pybot_threads)==0: print("No config files in 'pairs' directory. Nothing to read, please check documentation."); dl("No config files, exiting"); exit(1)
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

def leftprint(str):
    global leftwin
    leftwin.addstr(str+chr(10)+chr(13))
    leftwin.refresh()

# get current exchange balances for all threads
def getbalances():
    # always query 0.thread's pairs
    pybot_threads[0]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[0]["asset1"])["free"]
    pybot_threads[0]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[0]["asset2"])["free"]  
    # clear following threads balances
    for actthread in range(1,len(pybot_threads)):
        pybot_threads[actthread]["asset1balance"]=pybot_threads[actthread]["asset2balance"]="0"    
    # check following threads for duplicates
    for actthread in range(1,len(pybot_threads)):
        getasset1=getasset2=False
        pybot_threads[actthread]["asset1balance"]=pybot_threads[actthread]["asset2balance"]="0"
        # check previous threads, to not query an existing coin's balance multiple times
        for j in range(0,actthread):
            if pybot_threads[actthread]["asset1"]==pybot_threads[j]["asset1"]: pybot_threads[actthread]["asset1balance"]=pybot_threads[j]["asset1balance"]
            else: getasset1=True
            if pybot_threads[actthread]["asset2"]==pybot_threads[j]["asset2"]: pybot_threads[actthread]["asset2balance"]=pybot_threads[j]["asset2balance"]
            else: getasset2=True
            
        # if balance query needed
        if getasset1: pybot_threads[actthread]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset1"])["free"]
        if getasset2: pybot_threads[actthread]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset2"])["free"]
        #pybot_threads[actthread]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset1"])["free"]
        #pybot_threads[actthread]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[actthread]["asset2"])["free"]

# get candle data for 1 thread
def getcandles(threadno):
    global leftwin
    for j in range(0,500):
        pricedata[threadno][j]={
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
    
    leftprint("Getting candledata for "+pybot_threads[threadno]["asset1"]+pybot_threads[threadno]["asset2"]+' '+Client.KLINE_INTERVAL_15MINUTE)
    candles = client.get_klines(symbol=pybot_threads[threadno]["asset1"]+pybot_threads[threadno]["asset2"], interval=Client.KLINE_INTERVAL_15MINUTE)
    leftprint("Got "+str(len(candles))+" candles")
    leftprint("Calculating moving averages and indicators")
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
            if pricedata[threadno][i]["phigh"]>pricedata[threadno][i]["pclose"]*1.01: pricedata[threadno][i]["phigh"]=pricedata[threadno][i]["pclose"]*1.01
            if pricedata[threadno][i]["plow"]<pricedata[threadno][i]["pclose"]*0.99: pricedata[threadno][i]["plow"]=pricedata[threadno][i]["pclose"]*0.99

    # calc MAs
    for i in range(7,len(candles)):
        
        ma7sum=0
        for j in range(0,7):
            ma7sum+=pricedata[threadno][i-j]["pclose"]
        pricedata[threadno][i]["ma7"]=ma7sum/7
    for i in range(25,len(candles)):
        ma25sum=0
        for j in range(0,25):
            ma25sum+=pricedata[threadno][i-j]["pclose"]
        pricedata[threadno][i]["ma25"]=ma25sum/25
    for i in range(99,len(candles)):
        ma99sum=0
        for j in range(0,99):
            ma99sum+=pricedata[threadno][i-j]["pclose"]
        pricedata[threadno][i]["ma99"]=ma99sum/99

    # calc above&below indicators    
    for i in range(0,len(candles)):
        if pricedata[threadno][i]["pclose"]<pricedata[threadno][i]["ma7"] and pricedata[threadno][i]["pclose"]<pricedata[threadno][i]["ma25"] and pricedata[threadno][i]["pclose"]<pricedata[threadno][i]["ma99"]:
            pricedata[threadno][i]["below"]=True
        if pricedata[threadno][i]["pclose"]>pricedata[threadno][i]["ma7"] and pricedata[threadno][i]["pclose"]>pricedata[threadno][i]["ma25"] and pricedata[threadno][i]["pclose"]>pricedata[threadno][i]["ma99"]:
            pricedata[threadno][i]["above"]=True
                
        #print(i,pricedata[threadno][i]["popen"], pricedata[threadno][i]["ma7"],pricedata[threadno][i]["ma25"],pricedata[threadno][i]["ma99"],pricedata[threadno][i]["below"],pricedata[threadno][i]["above"])
    """
    # push everything to candledata.log
    fcd=open('log/candledata.log','a')
    for i in range(0,len(candles)):
        
        fcd.write(str(threadno)+' '+str(i)+' '+str(pricedata[threadno][i]["popen"])+' '
            +str(pricedata[threadno][i]["phigh"])+' '
            +str(pricedata[threadno][i]["plow"])+' '
            +str(pricedata[threadno][i]["pclose"])+'|'
            +str(pricedata[threadno][i]["ma7"])+' '+str(pricedata[threadno][i]["ma25"])+' '+str(pricedata[threadno][i]["ma99"])+'|B:'+str(pricedata[threadno][i]["below"])+' A:'+str(pricedata[threadno][i]["above"])+chr(13))

    fcd.close()
    """

#draw the price chart for 1 thread
def drawchart(threadno,stdscr):

    def calcy(theprice):
        chartwindowheight=chartwindow["top"]+chartwindow["height"]
        they=int(chartwindowheight-(theprice-pricemin)/charheightprice+0.5)
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
        for j in range(chartwindow["left"],chartwindow["width"],5):
            stdscr.addstr(chartwindow["top"]+int(chartwindow["height"]/5*i),j,U_BOX_HORZDOT, curses.A_DIM)
        stdscr.addstr(chartwindow["top"]+int(chartwindow["height"]/5*i),chartwindow["left"],str(round(pricemax-(pricemax-pricemin)/5*i,2)), curses.A_DIM)

    charheightprice=(pricemax-pricemin)/chartwindow["height"]
    dl (str(threadno)+' '+str(pricemin)+','+str(pricemax)+','+str(charheightprice))
    for i in range(0,chartwindow["width"]+1):
        actprice=pricedata[threadno][len(pricedata[threadno])-1-i]
        chartwindowheight=chartwindow["top"]+chartwindow["height"]
        chartwindowwidth =chartwindow["left"]+chartwindow["width"]

        # ^ and v indicators
        if actprice["above"]:
            stdscr.addstr(chartwindow["top"]-2,chartwindowwidth-i,U_ARROWUP,curses.color_pair(3) | curses.A_DIM)
            #stdscr.addstr(calcy(actprice["phigh"])-1,chartwindowwidth-i,U_ARROWUP,curses.color_pair(3) | curses.A_DIM)
            
        else:
            if actprice["below"]:
                stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,U_ARROWDOWN,curses.color_pair(2)| curses.A_DIM)    
                #stdscr.addstr(calcy(actprice["plow"])+1,chartwindowwidth-i,U_ARROWDOWN,curses.color_pair(2) | curses.A_DIM)
                
        for j in range(0,len(pybot_threads[actualthread]["orders"])):
            if int(pybot_threads[actualthread]["orders"][j]["transactTime"]/1000)>int(actprice["ptime"]) and int(pybot_threads[actualthread]["orders"][j]["transactTime"]/1000)<int(actprice["ptime"])+(15*60):
                if pybot_threads[actualthread]["orders"][j]["side"]=="SELL":
                    stdscr.addstr(chartwindow["top"]-2,chartwindowwidth-i,"S")
                    for y in range(chartwindow["top"],calcy(actprice["phigh"]),2): stdscr.addstr(y,chartwindowwidth-i,U_BOX_VERTH)
                else:
                    stdscr.addstr(chartwindowheight+2,chartwindowwidth-i,"B");
                    for y in range(calcy(actprice["plow"]),chartwindowheight+2,2): stdscr.addstr(y,chartwindowwidth-i,U_BOX_VERTH)
   


        # MAs
        stdscr.addstr(calcy(actprice["ma99"]),chartwindowwidth-i,"˙",curses.color_pair(7))
        stdscr.addstr(calcy(actprice["ma25"]),chartwindowwidth-i,"˙",curses.color_pair(8))
        stdscr.addstr(calcy(actprice["ma7"]),chartwindowwidth-i,"˙",curses.color_pair(9))

        # candle kanóc
        for j in range(calcy(actprice["phigh"]), calcy(actprice["plow"])+1):
            stdscr.addstr(j,chartwindowwidth-i,U_BOX_VERT,curses.A_DIM)                    


        # candle body
        # red
        if actprice["popen"]>actprice["pclose"]:    
            for j in range( calcy(actprice["popen"]), calcy(actprice["pclose"])+1): 
                stdscr.addstr(j,chartwindowwidth-i,U_CANDLEBODY,curses.color_pair(2))
        else:
            # green
            for j in range( calcy(actprice["pclose"]), calcy(actprice["popen"])+1): 
                stdscr.addstr(j,chartwindowwidth-i,U_CANDLEBODY,curses.color_pair(3))

        # write out min/max prices
        if actprice["phigh"]==pricemax:
            stdscr.addstr(chartwindow["top"]-1,chartwindowwidth-i,str(pricemax))
        if actprice["plow"]==pricemin:
            stdscr.addstr(chartwindowheight+1,chartwindowwidth-i,str(pricemin))


def draworders(stdscr):
    # order list
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+7 ,pybot_threads[actualthread]["asset1"])
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+16,pybot_threads[actualthread]["asset2"])
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+25,"Price")
    stdscr.addstr(orderwindow["top"], orderwindow["left"]+7+17+34,"P/L "+str(pybot_threads[actualthread]["minprofit"])+'%')
    for i in range(0,orderwindow["height"]):
        if len(pybot_threads[actualthread]["orders"])-1-i>=0:
            actorder=pybot_threads[actualthread]["orders"][len(pybot_threads[actualthread]["orders"])-1-i]
            ordercolor=curses.color_pair(0)
            # calc actual order qty-fees
            actbuyorderqty=calcbuyorderqty(actorder)
            actsellorderqty=calcsellorderqty(actorder)
            prevsellorderqty=calcsellorderqty(pybot_threads[actualthread]["orders"][len(pybot_threads[actualthread]["orders"])-1-i-1])
            # if sell, calculate P/L, and set corresponding color
            if actorder["side"]=="SELL":
                #profitloss=round((float(actorder["cummulativeQuoteQty"])/float(pybot_threads[actualthread]["orders"][len(pybot_threads[actualthread]["orders"])-1-i-1]["cummulativeQuoteQty"])-1)*100,2)
                profitloss=round((actsellorderqty/prevsellorderqty-1)*100,2)
                if profitloss>=0: ordercolor=curses.color_pair(3)
                else: ordercolor=curses.color_pair(2)
                # asset1
                stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+14
                    -len(str(float(actorder["executedQty"]))), str(float(actorder["executedQty"])),ordercolor)         
                # asset2
                stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+14+8
                    -len(str(actsellorderqty)), str(actsellorderqty),ordercolor)   

                stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+49-len(str(profitloss)),str(profitloss)+'%',ordercolor)
            else: # buy order
                # asset1
                stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+14
                    -len(str(actbuyorderqty)), str(actbuyorderqty),ordercolor)         
                # asset2
                stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+14+8
                    -len(str(round(float(actorder["cummulativeQuoteQty"]),2))), str(round(float(actorder["cummulativeQuoteQty"]),2)),ordercolor)                


            #dl(str(actorder))
            # buy/sell
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+2,actorder["side"],ordercolor)
            # date
            trtime=str(datetime.datetime.fromtimestamp(int(actorder["transactTime"]/1000), tz=timezone.utc ))
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7   ,trtime[:-9],ordercolor)

            # price
            stdscr.addstr(orderwindow["top"]+1+i, orderwindow["left"]+7+17+32
                -len(str(round(float(actorder["fills"][0]["price"]),2))), str(round(float(actorder["fills"][0]["price"]),2)),ordercolor)


def setwindowsizes():
    # setup "windows" in lame ways
    chartwindow["width"]=curses.COLS -1 - chartwindow["left"]  -1
    chartwindow["height"]=int(curses.LINES/2)-1
    statswindow["top"]=chartwindow["top"]+chartwindow["height"]+4
    statswindow["width"]=chartwindow["width"]
    statswindow["height"]=5
    leftwindow ["top"]=statswindow["top"]+statswindow["height"]+1
    leftwindow ["width"]=int(curses.COLS/2)
    leftwindow ["height"]=curses.LINES-leftwindow["top"]-1
    orderwindow["top"]=leftwindow ["top"]
    orderwindow["left"]=int(curses.COLS/2)+1
    orderwindow["width"]=leftwindow ["width"]
    orderwindow["height"]=leftwindow ["height"] 

def drawframe(stdscr):
    stdscr.clear()

     
    # draw corners
    stdscr.addstr(0,0,U_BOX_TOPLEFT); stdscr.addstr(0,curses.COLS-1,U_BOX_TOPRIGHT);stdscr.addstr(curses.LINES-1,0,U_BOX_BOTLEFT);
    # bottom right corner will raise an exception because addstr can't move the cursor to the next line    
    try: stdscr.addstr(curses.LINES-1,curses.COLS-1,U_BOX_BOTRIGHT);
    except: pass
    # edge lines
    for i in range(1,curses.COLS-1):
        stdscr.addstr(0,i,U_BOX_HORZ); stdscr.addstr(curses.LINES-1,i,U_BOX_HORZ);
        stdscr.addstr(statswindow["top"]-1,i,U_BOX_HORZ);stdscr.addstr(statswindow["top"]+statswindow["height"],i,U_BOX_HORZ)
    for i in range(1,curses.LINES-1):
        stdscr.addstr(i,0,U_BOX_VERT); stdscr.addstr(i,curses.COLS-1,U_BOX_VERT)
    #statswindow corners
        stdscr.addstr(statswindow["top"]-1,0,U_BOX_TLEFT);stdscr.addstr(statswindow["top"]+statswindow["height"],0,U_BOX_TLEFT)
        stdscr.addstr(statswindow["top"]-1,curses.COLS-1,U_BOX_TRIGHT);
        dl(str(statswindow["top"]))
        dl(str(statswindow["height"]))
        dl(str(curses.COLS-1))
        stdscr.addstr(statswindow["top"]+statswindow["height"],curses.COLS-1,U_BOX_TRIGHT)
    stdscr.addstr(statswindow["top"]-1,2,U_BOX_TRIGHT+' Stats '+U_BOX_TLEFT);
    
    # statusbar
    if settings["testmode"]: testwarningstr="- TEST! - | "
    else: testwarningstr=""
    stdscr.addstr(0,2,U_BOX_TRIGHT+' '+testwarningstr+'Thread '+str(actualthread)+' | '+pybot_threads[actualthread]["threadname"]+' | Pair: '+pybot_threads[actualthread]["asset1"]+'/'+pybot_threads[actualthread]["asset2"]+' '+U_BOX_TLEFT)
    stdscr.addstr(0,curses.COLS-16,U_BOX_TRIGHT+' '+"Refresh:    "+U_BOX_TLEFT)

    # bottom left window
    stdscr.addstr(leftwindow["top"]-1,leftwindow["left"]+leftwindow["width"],U_BOX_TUP);
    stdscr.addstr(leftwindow["top"]+leftwindow["height"],leftwindow["left"]+leftwindow["width"],U_BOX_TDOWN)
    for i in range(leftwindow["top"],leftwindow["top"]+leftwindow["height"]):
        stdscr.addstr(i,leftwindow["left"]+leftwindow["width"],U_BOX_VERT)

    #order window title
    stdscr.addstr(orderwindow["top"]-1,orderwindow["left"]+2,U_BOX_TRIGHT+" Orders "+U_BOX_TLEFT)

    #version
    stdscr.addstr(curses.LINES-1, curses.COLS-len(programversion)-6,U_BOX_TRIGHT+" "+programversion+" "+U_BOX_TLEFT)

# draw the whole screen
def drawwindow(stdscr):
    global actualthread
    global leftwin
    #dl(str(actualthread))
    # if window too small
    if curses.COLS<80 or curses.LINES<33:
        stdscr.clear(); stdscr.addstr(12,2,"Increase window size :) "); return
 
    setwindowsizes()
    drawframe(stdscr)
    drawchart(actualthread,stdscr)

    
    # thread stats
    stdscr.addstr(statswindow["top"],statswindow["left"]+40, str(pricedata[actualthread][len(pricedata[actualthread])-1]["pclose"]))
    stdscr.addstr(statswindow["top"],statswindow["left"],'Price: '+str(pybot_threads[actualthread]["currentprice"])+' '+pybot_threads[actualthread]["asset2"],curses.A_BOLD)
    stdscr.addstr(statswindow["top"]+1,statswindow["left"],'Balances:')
    stdscr.addstr(statswindow["top"]+2,statswindow["left"],pybot_threads[actualthread]["asset1"]+':')
    stdscr.addstr(statswindow["top"]+2,statswindow["left"]+7,str(pybot_threads[actualthread]["asset1balance"]))
    stdscr.addstr(statswindow["top"]+3,statswindow["left"],pybot_threads[actualthread]["asset2"]+':')
    stdscr.addstr(statswindow["top"]+3,statswindow["left"]+7,str(pybot_threads[actualthread]["asset2balance"]))
    # candles to buy/sell at right
    stdscr.addstr(statswindow["top"]  ,chartwindow["left"]+chartwindow["width"]-pybot_threads[actualthread]["candlestosell"]+1-17,"Candles to sell |")
    stdscr.addstr(statswindow["top"]+1,chartwindow["left"]+chartwindow["width"]-pybot_threads[actualthread]["candlestobuy"] +1-16,"Candles to buy |")
    # draw S and B indicators
    # SELL
    for i in range(0,pybot_threads[actualthread]["candlestosell"]):
        if pricedata[actualthread][len(pricedata[actualthread])-1-i]["above"]==True:
            stdscr.addstr(statswindow["top"],chartwindow["left"]+chartwindow["width"]-i,U_CHECKMARK,curses.color_pair(3))
    # BUY
    for i in range(0,pybot_threads[actualthread]["candlestobuy"]):
        if pricedata[actualthread][len(pricedata[actualthread])-1-i]["below"]==True:
            stdscr.addstr(statswindow["top"]+1,chartwindow["left"]+chartwindow["width"]-i,U_CHECKMARK,curses.color_pair(2))



    # order list
    draworders(stdscr)

    stdscr.refresh()
    #leftprint("")
    leftwin.clrtoeol()
    leftwin.refresh()


    



# calc 1 order-  substract trading fee amount
def calcbuyorderqty(order):
    quantity=0.0
    for i in range(0,len(order["fills"])):
        quantity += float(order["fills"][i]["qty"])-float(order["fills"][i]["commission"])
    # round to 8 decimals because of the fucking 64 bit float storing. It makes 0.00077900 from 0.0007790000000000001 which means 0.000779 finally
    return round(quantity,8)

# calc 1 order-  substract trading fee amount
def calcsellorderqty(order):
    quantity=float(order["cummulativeQuoteQty"])
    for i in range(0,len(order["fills"])):
        quantity -= float(order["fills"][i]["commission"])
    return round(quantity,8)
                

def loadorders(threadno):
    pybot_threads[threadno]["orders"]=[]
    if settings["testmode"]: tfilename="-test"
    else: tfilename=""
    orderfilename="pairs/"+pybot_threads[threadno]["threadname"]+tfilename+".trades"
    try:
        fo=open(orderfilename,'r')
    except FileNotFoundError:
        fo=open(orderfilename,'w'); fo.close(); fo=open(orderfilename,'r')
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



# main prog
def main(stdscr):
    global leftwin
    stdscr.refresh()
    global actualthread
    pressedkey=0

    stdscr.addstr('Windowsize:'+str(curses.COLS)+'x'+str(curses.LINES))
    if curses.COLS<80 or curses.LINES<33:
        curses.endwin();
        print("\n\nWindow ",curses.COLS,'x',curses.LINES)
        print("\n\nWindow size too small, exiting")

        exit()
    print("dummy")

    # Clear screen
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_GREEN)
    
    # MAs
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.curs_set(False)

    setwindowsizes()

    drawframe(stdscr)
    stdscr.refresh()
    leftwin=curses.newwin(leftwindow["height"], leftwindow["left"]+leftwindow["width"]-1, leftwindow["top"], leftwindow["left"])
    leftwin.scrollok(True)
    leftwin.refresh()
    


    stdscr.nodelay(1)
    while True:

        curses.curs_set(True)
        #stdscr.clear()
        #stdscr.refresh()        
        leftprint("Getting balances and symbol info")
        getbalances()        
        for i in range(0,len(pybot_threads)):
            leftprint(pybot_threads[i]["asset1"]+':'+pybot_threads[i]["asset1balance"])
            leftprint(pybot_threads[i]["asset2"]+':'+pybot_threads[i]["asset2balance"])
            #pybot_threads[i]["symbol_info"]=client.get_symbol_info(pybot_threads[i]["asset1"]+pybot_threads[i]["asset2"])
            #print(pybot_threads[i]["symbol_info"]["symbol"]+' Status: '+pybot_threads[i]["symbol_info"]["status"]+' SpotAllowed: '+str(pybot_threads[i]["symbol_info"]["isSpotTradingAllowed"])+chr(13))
            #dl(str(pybot_threads[i]["symbol_info"]))

        for actthread in range(0,len(pybot_threads)):
            curses.curs_set(True)
            getcandles(actthread)
            leftprint("Get current price")
            pybot_threads[actthread]["currentprice"] = float(client.get_avg_price(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])["price"])
            #dl(str(pybot_threads[actthread]["currentprice"]))
            curses.curs_set(False)

            oktobuycounter=0
            oktosellcounter=0
            #dl(str(pricedata))
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

            lastorder={}
            if len(pybot_threads[actthread]["orders"])==0:      # if there are no orders, we will start with a buy next
                lastorder["side"]="SELL"
            if len(pybot_threads[actthread]["orders"])>0:
                lastorder=pybot_threads[actthread]["orders"][len(pybot_threads[actthread]["orders"])-1]

            # buy order
            if oktobuycounter==pybot_threads[actthread]["candlestobuy"]+1 and lastorder["side"]=="SELL":
                saveorder(actthread,client.order_market_buy(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"], quoteOrderQty=pybot_threads[actthread]["quantity"]))
                pass

            # sell order with minprofit checking
            if (oktosellcounter==pybot_threads[actthread]["candlestosell"]+1 and lastorder["side"]=="BUY"
                    and pybot_threads[actthread]["currentprice"]>float(lastorder["fills"][0]["price"])*(100+pybot_threads[actthread]["minprofit"])/100):
                #saveorder(actthread,client.order_market_sell(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"], quantity=lastorder["executedQty"]))
                #dl(str(lastorder))

                coininfo = client.get_symbol_info(pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])
                dl(pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"])
                dl(str(coininfo["filters"]))
                sellingqty=0.0
                lastorderqty=calcbuyorderqty(lastorder)
                # round selling qty to the min needed number of decimals
                for i in range(0,len(coininfo["filters"])):
                    if coininfo["filters"][i]["filterType"]=='LOT_SIZE':
                        # rounding because of 64b floating point fuckery
                        sellingqty=round(lastorderqty - (lastorderqty % float(coininfo["filters"][i]["minQty"])),8)

                dl (str(sellingqty))
                dl (str(round(sellingqty,8)))
                saveorder(actthread,client.order_market_sell(symbol=pybot_threads[actthread]["asset1"]+pybot_threads[actthread]["asset2"], quantity=sellingqty))
            

        drawwindow(stdscr)
        
        start = time.time()
        elapsed=0
        while elapsed < refreshtime:
            elapsed = int(time.time() - start)
            
            stdscr.addstr(0,curses.COLS-5,"  ")
            stdscr.addstr(0,curses.COLS-5,str(60-elapsed))
            stdscr.refresh()
            time.sleep(0.25) 


            pressedkey=stdscr.getch()
            # num buttons
            if pressedkey>=48 and pressedkey<=57:
                dl("asdfasfasdf")
                if pressedkey-48<len(pybot_threads):
                    actualthread = pressedkey-48
                    #dl(str(actualthread))
                    drawwindow(stdscr)
                    leftwin.refresh()
                    stdscr.refresh()
                    

            # ESC
            if pressedkey==27:
                curses.endwin(); print();print(); print("Thanks for using",programname,programversion); print(); exit()
            # window resize
            if pressedkey==curses.KEY_RESIZE:
                curses.LINES, curses.COLS = stdscr.getmaxyx()
                drawwindow(stdscr)
                stdscr.refresh()

   

print("Initializing screen")

wrapper(main)



"""
11-23
USDT:  94.25064413
(0,0) to (curses.LINES - 1, curses.COLS - 1).


https://binance-docs.github.io/apidocs/spot/en/#introduction
https://testnet.binance.vision/
curl https://testnet.binance.vision/api/v3/exchangeInfo


pip install python-binance

https://python-binance.readthedocs.io/en/latest/market_data.html


curses:
https://docs.python.org/3/howto/curses.html

https://docs.python.org/3/library/curses.html#module-curses


eazybot:
https://www.youtube.com/watch?v=3ztxbDP5fNc&t=12s
"""


