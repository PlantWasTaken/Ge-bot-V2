import requests
import json
import time as t
import sys, os
import datetime
from operator import itemgetter


sys.setrecursionlimit(10000)

index = open("index.txt", "r")
bankmanagment = open("bank.json", "r")

data = ''
line_count = 0

headers = {

    'User-Agent' : 'Plant',
    'From' : 'Plant#6356'
}

temp = ''
#p_change = 0 #current price omcpared to yesterday price ot detrmine

index = open("index.txt", "r")

#list of all bought items n=[[[id0],[price0],[change0], [[id1],[price1],[change1]]]
def eval(data_l, f_i, p_change, data_5m): #evaulates all items in list, manages purchaes etc...
    #print(p_change)
    if(p_change >= -9): # price ranges from 0 to -9%
        if(p_change <= 0): # price ranges from 0 to -9%
            if(data_l['data'][f_i]['low'] >= 100):
                if(data_l['data'][f_i]['low'] <= 5000): #price is less than 5000
                    if(data_5m['data'][f_i]['lowPriceVolume'] >= 1000): #volume is more than 1000
                        bought_items.append([f_i, data_l['data'][f_i]['low'], p_change])
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass

def sell_items(bought_items, data_l): 
    log = open("log.txt", "a+") #opens log file
    current_prices = []

    for i in range(len(bought_items)):
        current_prices.append(data_l['data'][str(bought_items[i][0])]['high'])
    

    with open("bank.json", "r") as jsonFile:
        json_data_sell = json.load(jsonFile)                

    with open("bank.json", "w") as jsonFile: 
        for i in range(len(current_prices)):
            json_data_sell['items']['slot' + str(i+1)]['Current price'] = current_prices[i]

        #json_data_sell['items']['slot' + str(1)]['Current price'] = 1000 #test

        json.dump(json_data_sell, jsonFile, indent=4)

    with open("bank.json", "r") as jsonFile: #opens new instance of json file after appending prices
        json_data_sell = json.load(jsonFile)

    with open("bank.json", "w") as jsonFile:   #compares prices and decides to sell or hold
        for i in range(3):
            if(json_data_sell['items']['slot' + str(i+1)]['Price'] < ((json_data_sell['items']['slot' + str(i+1)]['Current price'])-(json_data_sell['items']['slot' + str(i+1)]['Current price']*0.02))):
                #print(json_data_sell['items']['slot' + str(i+1)]['Amount'], "AMOUNT")
                if(json_data_sell['items']['slot' + str(i+1)]['Amount'] > 0):

                    json_data_sell['items']['gp'] = (json_data_sell['items']['gp'] + (json_data_sell['items']['slot' + str(i+1)]['Current price']-(int(json_data_sell['items']['slot' + str(i+1)]['Current price']*0.01)))*json_data_sell['items']['slot' + str(i+1)]['Amount'])
                    json_data_sell['items']['slot' + str(i+1)]['Amount'] = 0 #changes amount after item has been sold
                    json_data_sell['items']['portfolio'] = (json_data_sell['items']['portfolio'])+(json_data_sell['items']['slot' + str(i+1)]['Price'])*(json_data_sell['items']['slot' + str(i+1)]['Amount']) #sets portfolio

                    now = datetime.datetime.now() #writing to log file
                    log.write("Sold " + str(json_data_sell['items']['slot' + str(i+1)]["Id"]) + " " + str(json_data_sell['items']['slot' + str(i+1)]["Current price"]) + " at : " + str(now.strftime("%Y-%m-%d %H:%M:%S") + "\n"))
                    
                
                else:
                    #print("NO0", i)
                    pass
            else:
                #print("NO", i)
                pass

        json_data_sell['items']['net'] = (json_data_sell['items']['gp']) + (json_data_sell['items']['portfolio']) #sets net value

        log.close() #closes log file
        json.dump(json_data_sell, jsonFile, indent=4)  


bought_items = [] #list of all bought items n=[[[id0],[price0],[change0], [[id1],[price1],[change1]]]

def buy_items(bought_items, data_l): #writes to json file
    #global bought_items #= ["2"][340][-3.24][cannon ball] | [id][price][change][name]
    log = open("log.txt", "a+") #openslo g file

    items_to_buy = [] #index of json file with 0 amount

    bought_items = sorted(bought_items, key=itemgetter(2), reverse=True) #sorts and picks out 3 biggest price falls

    with open("bank.json", "r") as jsonFile:
        json_data_buy = json.load(jsonFile)

        for i in range(3): #checks what slots are available
            if(json_data_buy['items']['slot' + str(i+1)]['Amount'] == 0):
                items_to_buy.append(i)
            else:
                pass

    del bought_items[0:len(bought_items)-3] #list filtering with respect to amount of avaiable slots

    with open("bank.json", "w") as jsonFile: #appends to jsonfile, buying items, current price, change
        j = 0
        for i in items_to_buy:  #filter thourhgt available items to decide what to append ot json
            json_data_buy['items']['slot' + str(i+1)]['Price'] = bought_items[j][1]    #item price, bought at price
            json_data_buy['items']['slot' + str(i+1)]['Change'] = bought_items[j][2]   #item change
            json_data_buy['items']['slot' + str(i+1)]['Id'] = bought_items[j][0] #item id

            json_data_buy['items']['slot' + str(i+1)]['Amount'] = int((json_data_buy['items']['gp'])/(len(items_to_buy))/bought_items[j][1]) #buys items
            j = j + 1


        
        if(len(items_to_buy) != 0): #moves money from a to b simulating purcahse
            for i in range(len(items_to_buy)):
                json_data_buy['items']['portfolio'] = (json_data_buy['items']['portfolio'])+(json_data_buy['items']['slot' + str(i+1)]['Price'])*(json_data_buy['items']['slot' + str(i+1)]['Amount'])
                json_data_buy['items']['gp'] = (json_data_buy['items']['gp'])-((json_data_buy['items']['slot' + str(items_to_buy[i]+1)]['Price'])*(json_data_buy['items']['slot' + str(items_to_buy[i]+1)]['Amount']))
                now = datetime.datetime.now() #writing to log file
                log.write("Bought id : " + str(bought_items[items_to_buy[i]]) + " at : " + str(now.strftime("%Y-%m-%d %H:%M:%S") + "\n"))
                                    
            json_data_buy['items']['net'] = (json_data_buy['items']['gp']) + (json_data_buy['items']['portfolio'])            
        else:
            pass

        log.close()
        json.dump(json_data_buy, jsonFile, indent=4)
    
    sell_items(bought_items, data_l)
    bought_items = []
    
    

def findItemPrice(): #finds all item prices from index.txt
    url1 = 'https://prices.runescape.wiki/api/v1/osrs/latest'
    url2 = 'https://prices.runescape.wiki/api/v1/osrs/5m'
    
    r1 = requests.get(url1, headers=headers)
    r2 = requests.get(url2, headers=headers)

    data_5m = r2.json()
    data_l = r1.json()

    for i in index:

        f_i = ''

        try:
            if(i[-1] == '\n'):
                
                item_price_5m = data_5m['data'][str(i[:-1])]['avgLowPrice']
                item_price_l = data_l['data'][str(i[:-1])]['low']
                f_i = str(i[:-1])
            else:
                item_price_5m = data_5m['data'][str(i)]['avgLowPrice']
                item_price_l = data_l['data'][str(i)]['low']
                f_i = str(i)

            if(item_price_5m == None):
                p_change = 0

            else:
                try:
                    p_change = (item_price_l-item_price_5m)/item_price_l*100
                except ZeroDivisionError:
                    p_change = 0

                eval(data_l, f_i, p_change, data_5m)
        except KeyError:
            pass

    buy_items(bought_items, data_l)
    #print(bought_items)
    #index.close()

rec = 2
for i in range(rec):
    findItemPrice()   
    print("Updating prices... " + str(int(((i+1)/rec)*100)) + "%" + "\nSafe to close")
    t.sleep(1)
    os.system('clear')

print("done")
