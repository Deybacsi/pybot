#!/usr/bin/python3


from binance.client import Client


# get candle data for 1 thread
def getcandles(threadno):
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
    fcd=open('candledata.log','a')
    for i in range(0,len(candles)):
        
        fcd.write(str(threadno)+' '+str(i)+' '+str(pricedata[threadno][i]["popen"])+' '
            +str(pricedata[threadno][i]["phigh"])+' '
            +str(pricedata[threadno][i]["plow"])+' '
            +str(pricedata[threadno][i]["pclose"])+'|'
            +str(pricedata[threadno][i]["ma7"])+' '+str(pricedata[threadno][i]["ma25"])+' '+str(pricedata[threadno][i]["ma99"])+'|B:'+str(pricedata[threadno][i]["below"])+' A:'+str(pricedata[threadno][i]["above"])+chr(13))

    fcd.close()
