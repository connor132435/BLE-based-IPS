import numpy as np

xdata = []
ydata = []
zdata = []

Bdata = []
Cdata = []
Ddata = []

distdata = []
bvectdata = []
 #However the data is formatted CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
f = open("data2.txt")
dataf = f.read()
data = dataf.split("\n")
f.close()
#print(data)
for i in range(len(data)):
  datapoint = data[i].split(" ")
  a = float(datapoint[0])
  b = float(datapoint[1])
  c = float(datapoint[2])
  d = float(datapoint[3])
  xdata.append(a)
  ydata.append(b)
  zdata.append(c)
  Bdata.append(-2 * a)
  Cdata.append(-2 * b)
  Ddata.append(-2 * c)
  distdata.append(d)
  bvectdata.append(d ** 2 - c ** 2 - b ** 2 - a ** 2)
#However the data is formatted CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


one = np.ones(len(xdata), dtype=float)
M = np.array([one, Bdata, Cdata, Ddata])
y = np.array(bvectdata)
y = y.transpose()  # vertical
M = M.transpose()  # vertical
def solv():
  try:
      N = np.linalg.solve(M, y)
  except:
      # ydata Not in column space
      K = np.linalg.pinv(M)
      N = K @ y
  print(N)
  return N


def eval_error():
  return np.linalg.norm(M @ N - y) ** 2



N = solv()
print('linear error')
print(eval_error())
