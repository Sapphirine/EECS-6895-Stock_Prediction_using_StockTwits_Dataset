import json
import datetime
import pandas as pd
import pandas_datareader.data as web

def processStock(stock_name):
    input_file = open("./stocks/"+stock_name+".json")
    ss = input_file.readline()
    each = json.loads(ss)
    print each

def get_stock_price_update(stock, start=None, end=None):
    if start != None:
        apple = web.DataReader(stock, "yahoo", start, end)
        return apple

if __name__ == "__main__":
    #processStock("AAPL")
    start = datetime.datetime(2017, 1, 17)
    end = datetime.datetime(2017, 1, 21)
    c = get_stock_price_update("AAPL",start,end)
    print(type(c.ix))
    for i in c:
        print(i)

   
