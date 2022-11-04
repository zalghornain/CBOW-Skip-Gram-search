import mysql.connector
import numpy as np
import time

sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

sourcecursor = sourcedb.cursor()

sourcecursor.execute("SELECT kata,vector_skip_gram FROM dictionary")

myresult = sourcecursor.fetchall()

dictionaryvectorkata = {}
#bikin dictionary kata dan vektor skip gram


for i in range(len(myresult)):
  intvektorkata = myresult[i][1]
  intvektorkata = intvektorkata.replace("[", "'")
  intvektorkata = intvektorkata.replace("]", "'")
  intvektorkata = np.fromstring(intvektorkata.strip('\'') ,sep=' ')
  dictionaryvectorkata[myresult[i][0]] = intvektorkata

katainput = input('Masukkan kata \n')
startAwalTime = time.time()
print()
print(katainput.split())
print()
katainput = katainput.split()
#print(len(katainput))
listcosinesimilarity = {}
jumlahkatavalid = 0
for i in range(len(katainput)):
  vectorkata = dictionaryvectorkata.get(katainput[i])
  #print(vectorkata)

  if vectorkata is not None:
    jumlahkatavalid = jumlahkatavalid + 1
    magnitudevectorkata = np.linalg.norm(vectorkata)
    print("vector kata untuk kata", katainput[i], "merupakan :\n", vectorkata)
    print()
    for j, (k, v) in enumerate(dictionaryvectorkata.items()):
      #print(k)
      #print(v)
      hasildotproduct = np.dot(vectorkata, v)
      magnitudev = np.linalg.norm(v)
      #kalo katanya cuma satu/kata pertama langsung input ke dalem listcosinesimilarity
      if i == 0:
        listcosinesimilarity[k] = hasildotproduct / (magnitudev * magnitudevectorkata)
        #if k == "james" :
        #  print("value untuk kata james di kata ke: ", i + 1 , " : ",  listcosinesimilarity[k])
        #  print("value untuk kata james setelah di total: ",listcosinesimilarity.get("james"))
        #  print()
      #kalo katanya ada banyak cari cosinesimilarity abis itu rata2in sama cosinesimilarity sebelumnya
      else:
        cosinesimilarity = hasildotproduct / (magnitudev * magnitudevectorkata)
        #cosine similaritynya di tambah tambah dulu
        #kalo kata pertama yang di input nggak valid
        if listcosinesimilarity.get(k) is None:
          listcosinesimilarity[k] = cosinesimilarity
        else:
          listcosinesimilarity[k] = (listcosinesimilarity.get(k) + cosinesimilarity)
        #if k == "james" :
        #  print("value untuk kata james di kata ke: ", i + 1 , " : ",  cosinesimilarity)
        #  print("value untuk kata james setelah di total: ",listcosinesimilarity.get("james"))
        #  print()
        
        #pas di kata terakhir di rata2in
        if i == len(katainput)-1:
          #rata-ratain berdasarkan jumlah kata yang ketemu di dictionary
          listcosinesimilarity[k] = listcosinesimilarity.get(k) / jumlahkatavalid
          
      #print("perkalian antara \n",vectorkata,"\n dengan \n",v,"\n merupakan : \n",listcosinesimilarity[k])
      #print()
  else :
    print("kata " + "\"" + katainput[i] + "\"" + " tidak ditemukan")
    print()
    #kalo kata terakhir yang di input nggak valid
    if i == len(katainput)-1:
      for j, (k, v) in enumerate(dictionaryvectorkata.items()):
        #rata-ratain berdasarkan jumlah kata yang ketemu di dictionary
        listcosinesimilarity[k] = listcosinesimilarity.get(k) / jumlahkatavalid

#kalo katanya satu munculin hasil tertinggi nomor 2 sampe 6 karena nomor 1 nya sama sama kata input
#print("value untuk kata james setelah di rata-ratakan", listcosinesimilarity.get("james"))
#print()
if len(katainput) == 1 :
  fivetopdict = sorted(listcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[1:6]
#kalo katanya banyak munculin hasil tertinggi 1 sampe 5
elif len(katainput) > 1 :
  fivetopdict = sorted(listcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[0:5]
print("5 kata paling mirip : \n",fivetopdict)
print()
waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))