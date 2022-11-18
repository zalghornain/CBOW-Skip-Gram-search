import mysql.connector
import numpy as np
import time
import re

katainput = input('Masukkan kata \n')

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

startAwalTime = time.time()
print()
print(katainput.split())
print()
katainput = katainput.split()
#print(len(katainput))
listcosinesimilarity = {}
katavalid = []
for i in range(len(katainput)):
  vectorkata = dictionaryvectorkata.get(katainput[i])
  #print(vectorkata)

  if vectorkata is not None:
    katavalid.append(katainput[i])
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
          listcosinesimilarity[k] = listcosinesimilarity.get(k) / len(katavalid)
          
      #print("perkalian antara \n",vectorkata,"\n dengan \n",v,"\n merupakan : \n",listcosinesimilarity[k])
      #print()
  else :
    print("kata " + "\"" + katainput[i] + "\"" + " tidak ditemukan")
    print()
    #kalo kata terakhir yang di input nggak valid
    if i == len(katainput)-1 and len(katavalid) >= 1:
      for j, (k, v) in enumerate(dictionaryvectorkata.items()):
        #rata-ratain berdasarkan jumlah kata yang ketemu di dictionary
        listcosinesimilarity[k] = listcosinesimilarity.get(k) / len(katavalid)


#kalo katanya satu munculin hasil tertinggi nomor 2 sampe 6 karena nomor 1 nya sama sama kata input
#print("value untuk kata james setelah di rata-ratakan", listcosinesimilarity.get("james"))
#print()
if len(katavalid) == 1 :
  fivetopdict = sorted(listcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[1:6]
#kalo katanya banyak munculin hasil tertinggi nomor 1 sampe 5
elif len(katavalid) > 1 :
  fivetopdict = sorted(listcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[0:5]
elif len(katavalid) < 1 :
  quit()
print("5 kata paling mirip : \n",fivetopdict)
print()
print("tekan enter")
wait=input()
print()

sourcecursor.execute("SELECT sumber_url,content FROM text")

dictionarykemunculan= {}
dictionarykatavalidrelevan = {}

listtext = sourcecursor.fetchall()
#listtext[index][kolom]
nilaidokumen = 0
print(len(listtext))
for i in range(len(listtext)):
  for j in range(len(katavalid)):
    print("sumber ke : ", i + 1, listtext[i][0])
    print(katavalid[j])
    #cari kata valid di kolom content dengan menggunakan regular expression
    #print(len(re.findall('\\b'+katavalid[j]+'\\b',listtext[i][1])))
    #itung jumlah kemunculan
    jumlahkemunculanvalid = len(re.findall('\\b'+katavalid[j]+'\\b',listtext[i][1]))  
    #taro [katainputvalid : jumlah kemunculan] pada dictionarykatavalidrelevan
    dictionarykatavalidrelevan[katavalid[j]] = (jumlahkemunculanvalid)
    #itung nilai dokumen dengan jumlah kemunculan katainput * 10
    nilaidokumen += jumlahkemunculanvalid * 10
    print("poin kata input : ", 10)
    print("jumlah kemunculan : ", jumlahkemunculanvalid)
    print("nilai dokumen : ", nilaidokumen)
    print()
  poinkatarelevan = 5
  for k in range(len(fivetopdict)):
    print("sumber ke : ", i + 1, listtext[i][0])
    print(fivetopdict[k][0])
    #print(listtext[i][1].find(fivetopdict[k][0]))
    #cari kata relevan di kolom content dengan menggunakan regular expression
    #print(len(re.findall('\\b'+fivetopdict[k][0]+'\\b',listtext[i][1])))
    #itung jumlah kemunculan
    jumlahkemunculankatarelevan = len(re.findall('\\b'+fivetopdict[k][0]+'\\b',listtext[i][1]))
    #taro [katarelevan : jumlah kemunculan] pada dictionarykatavalidrelevan
    dictionarykatavalidrelevan[fivetopdict[k][0]] = (jumlahkemunculankatarelevan) 
    #itung nilai dokumen dengan jumlah kemunculan kata relevan * 5, kata relevan * 4, dst 
    nilaidokumen += jumlahkemunculankatarelevan * poinkatarelevan
    print("poin kata relevan : ", poinkatarelevan)
    print("jumlah kemunculan : ", jumlahkemunculankatarelevan)
    print("nilai dokumen : ", nilaidokumen)
    print()
    poinkatarelevan = poinkatarelevan - 1
  #taro ["nilai dokumen" : int(nilai) ] pada dictionarykatavalidrelevan
  dictionarykatavalidrelevan["nilai dokumen"] = nilaidokumen
  #reset nilai dokumen
  nilaidokumen = 0
  print(dictionarykatavalidrelevan)
  print()
  print()
  #bikin dictionary nested [sumber : {kata input : jumlah, kata relevan : jumlah, nilai dokumen : nilai}]
  dictionarykemunculan[listtext[i][0]] = dictionarykatavalidrelevan
  dictionarykatavalidrelevan= {}

limadokumenpalingrelevan = sorted(dictionarykemunculan.items(), key=lambda item: item[1]["nilai dokumen"], reverse=True)[0:5]
for i in range(len(limadokumenpalingrelevan)):
  print(limadokumenpalingrelevan[i])
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))