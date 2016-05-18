import datetime
import time
import os.path
import logging

dataPath = "/home/infra/Strategy_Proj/Bin/datas"

startDateStr = "20110101"
endDateStr = "20121231"
#endDateStr = "20141231"

stockList = [line.split(",")[0] for line in open("AllAShareStock.csv" )]
#stockList = ["300359.SZ"]
processDate = datetime.datetime.strptime(startDateStr, "%Y%m%d") - datetime.timedelta(days=1)
endDate = datetime.datetime.strptime(endDateStr, "%Y%m%d")

inventories = {}
transactions = []
preCloseMap = {}

buyLot = 200000

appName = "HighLimitTest"
logger = logging.getLogger(appName)
logger.setLevel("DEBUG")
fh = logging.FileHandler(appName + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s|%(levelname)s:%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

class Transaction:
    enterTS = datetime.datetime.now()
    leaveTS = datetime.datetime.now()
    enterPrice = 0.0
    leavePrice = 0.0
    qty = 0
    stock = ""

    def __init__(self, enterTS, leaveTS, enterPrice, leavePrice, qty, stock):
        self.enterTS = enterTS
        self.leaveTS = leaveTS
        self.enterPrice = enterPrice
        self.leavePrice = leavePrice
        self.qty = qty
        self.stock = stock


class InventoryItem:
    enterTS = datetime.datetime.now()
    enterPrice = 0.0
    qty = 0

    def __init__(self, enterTS, enterPrice, qty):
        self.enterTS = enterTS
        self.enterPrice = enterPrice
        self.qty = qty

def tail(f, lines):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
    # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

def getLastLine(dataFile):
    return tail(open(dataFile, "r"), 1)

def genTS(date, ts):
    [h, m, s] = ts.split(":")
    date = date + datetime.timedelta(hours = int(h), minutes = int(m), seconds = int(s))
    return date

def trySell(dataFile, stock, date, preClose):
    for line in open(dataFile):
        dataLine = line.split()
        latest = float(dataLine[0])
        ts = dataLine[8]

        if (compareTS(ts, "09:30:00")):
            continue

        latestPercent = (latest - preClose) / preClose
        if (latestPercent < 0.09 and latestPercent > -0.096):
            item = inventories[stock]
            #TODO add transction and impact
            transactions.append(Transaction(item.enterTS, genTS(date, ts), item.enterPrice, latest, item.qty, stock))
            inventories.pop(stock, None)
            logger.info("%s %s sell %d shares of %s, at price %f",
                    datetime.datetime.strftime(date, "%Y_%m_%d"), ts, item.qty, stock, latest)
            break;

def compareTS(tsStr1, tsStr2):
    return datetime.datetime.strptime(tsStr1, "%H:%M:%S") < datetime.datetime.strptime(tsStr2, "%H:%M:%S")


def tryBuy(dataFile, stock, date, preClose):
    for line in open(dataFile):
        dataLine = line.split()
        latest = float(dataLine[0])
        ts = dataLine[8]

        if (compareTS(ts,"09:30:00")):
            continue

        latestPercent = (latest - preClose) / preClose

        if (latestPercent > 0.094 and latestPercent < 0.0985):
            #TODO round to nearest 100
            qty = ((int)(buyLot / latest / 100)) * 100
            #TODO check here only buy once
            inventories[stock] = InventoryItem(genTS(date, ts), latest, qty)
            logger.info("%s %s buy %d shares of %s, at price %f", datetime.datetime.strftime(date, "%Y_%m_%d"),
                     ts, qty, stock, latest)
            break

        if (not compareTS(ts, "10:30:00")):
            break;

    lastLine = getLastLine(dataFile)
    preClose = float(lastLine.split()[0])
    preCloseMap[stock] = preClose

def dumpTranscations():
    file = open("result_" + startDateStr + "_" + endDateStr, "w")
    for tran in transactions:
        file.write("%s,%s,%f,%s,%f,%d\n" % (tran.stock,
            datetime.datetime.strftime(tran.enterTS, "%Y_%m_%d %H:%M:%S"), tran.enterPrice,
            datetime.datetime.strftime(tran.leaveTS, "%Y_%m_%d %H:%M:%S"), tran.leavePrice, tran.qty))

while processDate <= endDate:
      for stock in stockList:
        #TODO need to fix dividend issue update qty in inventory or fix preclose price
        [tickerCode, exchange] = stock.split(".")
        code = exchange + tickerCode
        if exchange  == "SH":
            suffix = "_SSE_L1.txt"
        else:
            suffix = "_SZSE_L1.txt"

        dataFile = dataPath + "/" + code + "/" + processDate.strftime('%Y%m%d') + "_" + code + suffix

        if not os.path.isfile(dataFile):
            continue

        if (not stock in preCloseMap.keys()):
            lastLine = getLastLine(dataFile)
            preCloseMap[stock] = float(lastLine.split()[0])
            continue

        if stock in inventories.keys():
            trySell(dataFile, stock, processDate, preCloseMap[stock])
        else:
            tryBuy(dataFile, stock, processDate, preCloseMap[stock])

    print "complete ", processDate
    processDate = processDate + datetime.timedelta(days=1)

dumpTranscations()
