import tushare as ts
import datetime

stockList = [line.split(",")[0] for line in open("AllAShareStock.csv" )]

allStockBasic = ts.get_stock_basics();

for stock in stockList:
    stockCode = stock[0:6]
    dateStr = str(allStockBasic.ix[stockCode]['timeToMarket'])
    y = dateStr[0:4]
    m = dateStr[4:6]
    d = dateStr[6:8]

    print dateStr
    print stock
    df = ts.get_h_data(stock, autype=None, start=y + "-" + m + "-" + d);

    print "df print"
    print df
    print "df end"

    for idx, row in df.iterrows():
        dateStr = row[0].strftime("%Y%m%d")
        filePath = "./DayData/" + stock + "/" + dateStr
        print ','.join([row[1], row[2], row[3], row[4]])
        raw_input()

