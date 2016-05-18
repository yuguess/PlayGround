import datetime
import os

dataPath = "/home/infra/Strategy_Proj/Bin/datas"
resPath = "/home/yuguess/ProcessFile/"
startDateStr = "20110101"
endDateStr = "20150101"
#stockList = ["300314.SZ"]
stockList = [line.split(",")[0] for line in open("../CSVConfig/AllAShareStock.csv" )]
processDate = datetime.datetime.strptime(startDateStr, "%Y%m%d")
endDate = datetime.datetime.strptime(endDateStr, "%Y%m%d")
start = "09:30:00"

precision = 300

def stringToDate(hmsStr):
  #HH:MM:SS format
  return datetime.datetime.strptime(hmsStr, "%H:%M:%S")

def dumpLine(buf, writeFile, dateStr, slideStart, slideEnd):
  stats = buf.pop()
  line = '%s,%s,%s,%.4f,%.4f,%.4f,%.4f\n' % (dateStr,
    datetime.datetime.strftime(slideStart, "%H:%M:%S"),
    datetime.datetime.strftime(slideEnd, "%H:%M:%S"),
  stats["open"], stats["high"], stats["low"], stats["close"])
  writeFile.write(line)

def processFile(date, stock, dataFile, precision, start):
  slideStart = stringToDate(start)
  slideEnd = slideStart + datetime.timedelta(seconds=precision)
  dataDir = resPath + date
  buf = []

  if (not os.path.exists(dataDir)):
    os.makedirs(dataDir)
  discreteFile = open(dataDir + "/" + stock, "w")

  for line in open(dataFile):
    fields = line.split()
    ts = stringToDate(fields[8])
    latest = float(fields[0])

    if (ts < slideStart):
      continue

    while ts >= slideEnd:
      if len(buf) == 1:
        dumpLine(buf, discreteFile, date, slideStart, slideEnd)

      slideStart = slideStart + datetime.timedelta(seconds=precision)
      slideEnd = slideEnd + datetime.timedelta(seconds=precision)

    if (len(buf) == 0):
      #print "processing " + datetime.datetime.strftime(slideStart,
      #    "%H:%M:%S") + "~" + datetime.datetime.strftime(slideEnd, "%H:%M:%S")
      buf.append({"open":0, "high":0, "low":10000, "close":0})
      buf[0]["open"] = latest

    buf[0]["high"] = max(latest, buf[0]["high"])
    buf[0]["low"] = min(latest, buf[0]["low"])
    buf[0]["close"] = latest


  if len(buf) == 1:
    dumpLine(buf, discreteFile, date, slideStart, slideEnd)
  discreteFile.close()


while processDate <= endDate:
  dateStr = processDate.strftime('%Y%m%d')
  print "processing ", dateStr
  for stock in stockList:
  #TODO need to fix dividend issue update qty in inventory or fix preclose price
    [tickerCode, exchange] = stock.split(".")
    code = exchange + tickerCode
    if exchange  == "SH":
      suffix = "_SSE_L1.txt"
    else:
      suffix = "_SZSE_L1.txt"

    dataFile = dataPath + "/" + code + "/" + dateStr + "_" + code + suffix

    if not os.path.isfile(dataFile):
      continue

    processFile(dateStr, stock, dataFile, precision, start)

  processDate = processDate + datetime.timedelta(days=1)
