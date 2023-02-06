import mysql.connector
import numpy as np
import time
import re

katainput = input('Masukkan kata \n')
print()

sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

sourcecursor = sourcedb.cursor()

sourcecursor.execute("SELECT kata,vector_cbow FROM dictionary")

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
#print()
#print(katainput.split())
#print()
katainput = katainput.split()
#print(katainput)
#print(len(katainput))
dictcosinesimilarity = {}
dictcosinesimilarity2 = {}
katavalid = []
#print(len(katainput))
if len(katainput) != 2 and len(katainput) != 4 :
    print("jumlah kata yang dimasukkan tidak sesuai, silahkan jalankan ulang program")
    print()
    quit()
for i in range(len(katainput)):
  vectorkata = dictionaryvectorkata.get(katainput[i])
  #print(vectorkata)
  #input()
  if vectorkata is not None:
    katavalid.append(katainput[i])
    magnitudevectorkata = np.linalg.norm(vectorkata)
    #print("vector kata untuk kata", katainput[i], "merupakan :\n", vectorkata)
    #print()
    for j, (k, v) in enumerate(dictionaryvectorkata.items()):
      hasildotproduct = np.dot(vectorkata, v)
      magnitudev = np.linalg.norm(v)
      if i == 0 :
        dictcosinesimilarity[k] = (hasildotproduct / (magnitudev * magnitudevectorkata))
      #pas di kata terakhir sum terus di rata2in
      elif i == 1:
        dictcosinesimilarity[k] = dictcosinesimilarity.get(k) + (hasildotproduct / (magnitudev * magnitudevectorkata))
        #rata-ratain berdasarkan jumlah kata yang ketemu di dictionary
        dictcosinesimilarity[k] = dictcosinesimilarity.get(k) / 2
        #print(dictcosinesimilarity.get(k))
        #input()
      elif i == 2:
        dictcosinesimilarity2[k] = (hasildotproduct / (magnitudev * magnitudevectorkata))
      elif i == 3:
        dictcosinesimilarity2[k] = dictcosinesimilarity2.get(k) + (hasildotproduct / (magnitudev * magnitudevectorkata))
        #rata-ratain berdasarkan jumlah kata yang ketemu di dictionary
        dictcosinesimilarity2[k] = dictcosinesimilarity2.get(k) / 2
        #print(dictcosinesimilarity.get(k))
        #input()
  else :
    print("kata " + "\"" + katainput[i] + "\"" + " tidak ditemukan")
    print()
    quit()

if len(katavalid) == 2 :
  #exclude kata input dari top five dict
  for i in range(len(katavalid)):
    del dictcosinesimilarity[katavalid[i]]
  fivetopdict = sorted(dictcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[0:5]
elif len(katavalid) > 2 :
  for i in range(len(katavalid)):
    del dictcosinesimilarity[katavalid[i]]
    del dictcosinesimilarity2[katavalid[i]]
  fivetopdict = sorted(dictcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[0:5]
  fivetopdict2 = sorted(dictcosinesimilarity2.items(), key=lambda item: item[1], reverse=True)[0:5]


#print("5 kata paling mirip pasangan pertama : \n",fivetopdict)
if len(katavalid) > 2 :
  #print("5 kata paling mirip pasangan kedua : \n",fivetopdict2)
  pass
#print()
#print("tekan enter")
#input()
#print()

sourcecursor.execute("SELECT sumber_url,content FROM text")

dictionarykemunculan= {}
dictionarykatavalidrelevan = {}

listtext = sourcecursor.fetchall()
#listtext[index][kolom]
nilaidokumen = 0

#pake 20% data sisa doang
#kurang satu karena index mulai dari 0
#cek lagi range atas harusnya di exclude bukan di include
del listtext[0:round(len(listtext) * 0.8)-1]

#print(len(listtext))
for i in range(len(listtext)):
  #print("sumber ke : ", i + 1, listtext[i][0])
  #print(katavalid[0])
  #print(katavalid[1])
  #cari kata valid di kolom content dengan menggunakan regular expression
  #print(len(re.findall('\\b'+katavalid[j]+'\\b',listtext[i][1])))
  #itung jumlah kemunculan
  satudua = katavalid[0] + " " + fivetopdict[0][0] + " " + katavalid[1]
  duasatu = katavalid[1] + " " + fivetopdict[0][0] + " " + katavalid[0]
  #print(satudua)
  #print(duasatu)
  if len(katavalid) > 2:
    #print(katavalid[2])
    #print(katavalid[3])
    tigaempat = katavalid[2] + " " + fivetopdict2[0][0] + " " + katavalid[3]
    empattiga = katavalid[3] + " " + fivetopdict2[0][0] + " " + katavalid[2]
    #print(tigaempat)
    #print(empattiga)
  jumlahkemunculansatudua = len(re.findall('\\b'+ satudua +'\\b',listtext[i][1]))  
  jumlahkemunculanduasatu = len(re.findall('\\b'+ duasatu +'\\b',listtext[i][1]))
  #taro [katainputvalid : jumlah kemunculan] pada dictionarykatavalidrelevan
  dictionarykatavalidrelevan[satudua] = (jumlahkemunculansatudua)
  dictionarykatavalidrelevan[duasatu] = (jumlahkemunculanduasatu)
  if len(katavalid) > 2:
    jumlahkemunculantigaempat = len(re.findall('\\b'+ tigaempat +'\\b',listtext[i][1]))  
    jumlahkemunculanempattiga = len(re.findall('\\b'+ empattiga +'\\b',listtext[i][1]))
    dictionarykatavalidrelevan[tigaempat] = (jumlahkemunculantigaempat)
    dictionarykatavalidrelevan[empattiga] = (jumlahkemunculanempattiga)
  nilaidokumen = 1 * jumlahkemunculansatudua + 1 * jumlahkemunculanduasatu
  if len(katavalid) > 2:
    nilaidokumen += 1 * jumlahkemunculantigaempat + 1 * jumlahkemunculanempattiga
  dictionarykatavalidrelevan["nilai dokumen"] = nilaidokumen
  #print(nilaidokumen)

  #print(dictionarykatavalidrelevan)
  #print()
  #print()
  #bikin dictionary nested [sumber : {kata input : jumlah, kata relevan : jumlah, nilai dokumen : nilai}]
  dictionarykemunculan[listtext[i][0]] = dictionarykatavalidrelevan
  dictionarykatavalidrelevan= {}

limadokumenpalingrelevan = sorted(dictionarykemunculan.items(), key=lambda item: item[1]["nilai dokumen"], reverse=True)[0:5]
for i in range(len(limadokumenpalingrelevan)):
  #print(limadokumenpalingrelevan[i])
  print("Hasil dokumen ranking", i+1,":", limadokumenpalingrelevan[i][0])
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))