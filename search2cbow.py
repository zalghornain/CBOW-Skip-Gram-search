import mysql.connector
import numpy as np
import time
import re
import random

katainput = input('Masukkan kata \n')
startAwalTime = time.time()
print()

sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

sourcecursor = sourcedb.cursor()

sourcecursor.execute("SELECT kata, one_hot_encode, vector_cbow FROM dictionary")

myresult = sourcecursor.fetchall()

dictionaryonehotencodekata = {}
#bikin dictionary kata dan vektor skip gram

sourcecursor.execute("SELECT matrix_weight_input,matrix_weight_output,kata_unik,hidden_layer FROM weight WHERE metode='cbow' GROUP BY ID = (SELECT MAX(ID) FROM weight)")
weight = sourcecursor.fetchone()
matrixweightinput = weight[0]
matrixweightinput = matrixweightinput.replace("[", "'")
matrixweightinput = matrixweightinput.replace("]", "'")
#weight = kataunik x hiddenlayer
matrixweightinput = np.fromstring(matrixweightinput.strip('\'') ,sep=' ').reshape((weight[2], weight[3]))

matrixweightoutput = weight[1]
matrixweightoutput = matrixweightoutput.replace("[", "'")
matrixweightoutput = matrixweightoutput.replace("]", "'")
#weight = hiddenlayer x kataunik
matrixweightoutput = np.fromstring(matrixweightoutput.strip('\'') ,sep=' ').reshape((weight[3], weight[2]))

for i in range(len(myresult)):
  onehotencode = myresult[i][1]
  onehotencode = onehotencode.replace(" ", "")
  onehotencode = onehotencode.replace(",", "")
  onehotencode = onehotencode.replace("[", "")
  onehotencode = onehotencode.replace("]", "")
  onehotencode = np.asarray(list(onehotencode)).astype(np.float64)
  dictionaryonehotencodekata[myresult[i][0]] = onehotencode


katainput = katainput.split()
if len(katainput) != 2 :
    print("jumlah kata yang dimasukkan tidak sesuai, silahkan jalankan ulang program")
    print()
    quit()

onehotencodekata = dictionaryonehotencodekata.get(katainput[0])
onehotencodekata2 = dictionaryonehotencodekata.get(katainput[1])
if onehotencodekata is not None and onehotencodekata2 is not None:
  katainput[0]
  katainput[1]
  hiddenlayer = (1/2) * np.dot(np.transpose(matrixweightinput),(onehotencodekata + onehotencodekata2))
  uj = np.dot(np.transpose(matrixweightoutput),hiddenlayer)
  expuj = np.exp(uj - np.max(uj))
  yj = expuj/np.sum(expuj)
  listonehotencodekata = list(dictionaryonehotencodekata)
  katatengah = listonehotencodekata[np.argmax(yj)]
  listkatatengah = []
  i=0
  while i <= 5 :
    i+=1
    listkatatengah.append(listonehotencodekata[np.argmax(yj)])
    yj[np.argmax(yj)] = 0
  #print("kata tengah merupakan : ", katatengah)
  #print("5 kata tengah tertinggi merupakan : ", listkatatengah)
  #print("tekan enter")
  #input()
elif onehotencodekata is None :
  print("kata " + "\"" + katainput[0] + "\"" + " tidak ditemukan")
  print()
  quit()
elif onehotencodekata2 is None :
  print("kata " + "\"" + katainput[1] + "\"" + " tidak ditemukan")
  print()
  quit()


sourcecursor.execute("SELECT sumber_url,content FROM text")

dictionarykemunculan= {}
dictionarykatavalidrelevan = {}

listtext = sourcecursor.fetchall()
#listtext[index][kolom]
nilaidokumen = 0

for i in range(len(listtext)):
  #cari kata valid di kolom content dengan menggunakan regular expression
  #itung jumlah kemunculan
  satudua = katainput[0] + " " + katatengah + " " + katainput[1]
  duasatu = katainput[1] + " " + katatengah + " " + katainput[0]
  jumlahkemunculansatudua = len(re.findall('\\b'+ satudua +'\\b',listtext[i][1]))  
  jumlahkemunculanduasatu = len(re.findall('\\b'+ duasatu +'\\b',listtext[i][1]))
  #taro [katainputvalid : jumlah kemunculan] pada dictionarykatavalidrelevan
  dictionarykatavalidrelevan[satudua] = (jumlahkemunculansatudua)
  dictionarykatavalidrelevan[duasatu] = (jumlahkemunculanduasatu)
  nilaidokumen = 1 * jumlahkemunculansatudua + 1 * jumlahkemunculanduasatu
  dictionarykatavalidrelevan["nilai dokumen"] = nilaidokumen

  #bikin dictionary nested [sumber : {kata input : jumlah, kata relevan : jumlah, nilai dokumen : nilai}]
  dictionarykemunculan[listtext[i][0]] = dictionarykatavalidrelevan
  dictionarykatavalidrelevan= {}

listdictionarykemunculan = list(dictionarykemunculan)
limadokumenpalingrelevan = sorted(dictionarykemunculan.items(), key=lambda item: item[1]["nilai dokumen"], reverse=True)[0:5]
for i in range(len(limadokumenpalingrelevan)):
  if limadokumenpalingrelevan[i][1]["nilai dokumen"] == 0 :
    #print("Hasil dokumen :", limadokumenpalingrelevan[random.randrange(1,70)][0])
    print("Hasil dokumen :", listdictionarykemunculan[random.randrange(1,70)])
  else :
    #print("Hasil dokumen :", limadokumenpalingrelevan[i][0])
    print(limadokumenpalingrelevan[i])
  
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))