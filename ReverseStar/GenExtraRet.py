import datetime
import os

dataPath = "/home/yuguess/ProcessFile"
resPath = "/home/yuguess/RelativeRet"

startDateStr = "20110101"
endDateStr = "20110110"

#index = "399905.SZ"
index = "300059.SZ"
#stockList = [line.split(",")[0] for line in open("AllAShareStock.csv" )]
stockList = ["300104.SZ"]
preCloseMap = {}

processDate = datetime.datetime.strptime(startDateStr, "%Y%m%d")
endDate = datetime.datetime.strptime(endDateStr, "%Y%m%d")

def dumpRelativeRet(rltvRt, dateStr, stockStr, writeFile):
  line = '%s,%.4f,%.4f,%.4f,%.4f\n' % (dateStr, rltvRt[0], max(rltvRt), min(rltvRt), rltvRt[-1])
  writeFile.write(line)

def processFile(dateStr, stockStr, dataFile, idxMap):
  rltvRt = []
  preClose = preCloseMap[stockStr]
  writeFile = open(resPath + "/" + stockStr, "w")

  for line in open(dataFile):
    fields = line.split(',')
    openPrice = float(fields[3])
    if fields[1] in idxMap.keys():
      ret = openPrice / preClose - 1
      rltvRt.append(ret - idxMap[fields[1]])

  preCloseMap[stockStr] = float(fields[6])
  dumpRelativeRet(rltvRt, dateStr, stockStr, writeFile);

def loadIndexData(dataFile, stock):
  preClose = preCloseMap[stock]
  idxMap = {}
  for line in open(dataFile, "r"):
    fields = line.split(',')
    idxMap[fields[1]] = float(fields[3]) / preClose - 1

  preCloseMap[fields[1]] = float(fields[3])
  return idxMap

def getDataFileStr(dateStr, stockStr):
  return dataPath + "/" + dateStr + "/" + stockStr

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

while processDate <= endDate:
  dateStr = processDate.strftime('%Y%m%d')
  print "processing ", dateStr

  if (not index in preCloseMap.keys()):
    if os.path.isfile(getDataFileStr(dateStr, index)):
      preCloseMap[index] = float(getLastLine(getDataFileStr(dateStr, index)).split(',')[3])
  else:
    dataFile = getDataFileStr(dateStr, index)
    if (os.path.isfile(dataFile)):
      idxMap = loadIndexData(dataFile, index)

      for stock in stockList:
        dataFile = getDataFileStr(dateStr, stock)
        if os.path.isfile(dataFile):
          if (not stock in preCloseMap.keys()):
            preCloseMap[stock] = float(getLastLine(dataFile).split(',')[3])
          else:
            processFile(dateStr, stock, getDataFileStr(dateStr, stock), idxMap)

  processDate = processDate + datetime.timedelta(days=1)
