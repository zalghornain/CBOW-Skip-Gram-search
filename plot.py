import matplotlib.pyplot as plt
import numpy as np
import mysql.connector


sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

sourcecursor = sourcedb.cursor()

#ambil data dari dbcrawl, hasil tools fathan
sourcecursor.execute("SELECT kata,vector_skip_gram FROM dictionary")

myresult = sourcecursor.fetchall()

print(sourcecursor.rowcount)

dictionaryvectorkata = {}

for i in range(len(myresult)):
  intvektorkata = myresult[i][1]
  intvektorkata = intvektorkata.replace("[", "'")
  intvektorkata = intvektorkata.replace("]", "'")
  intvektorkata = np.fromstring(intvektorkata.strip('\'') ,sep=' ')
  #print(intvektorkata)
  #print(intvektorkata.shape)
  if i == 0 :
    arrayall = np.asarray(intvektorkata).reshape(1,400)
  else :
    arrayall = np.concatenate((arrayall, np.asarray(intvektorkata).reshape(1,400)), axis=0)


print(arrayall.shape)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

x = arrayall[:,0]
y = arrayall[:,1]

ax.scatter(x, y)
plt.show()