cnt = 0
rSum = 0.0
for line in open("ttt1"):
  rSum +=float(line)
  cnt = cnt +1

print rSum / cnt
