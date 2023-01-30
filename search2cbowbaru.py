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

sourcecursor.execute("SELECT kata, one_hot_encode, vector_cbow FROM dictionary")

myresult = sourcecursor.fetchall()

dictionaryonehotencodekata = {}
#bikin dictionary kata dan vektor skip gram

sourcecursor.execute("SELECT matrix_weight_input,matrix_weight_output,kata_unik,hidden_layer FROM weight WHERE ID = (SELECT MAX(ID) FROM weight) AND metode='cbow'")
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

#print(matrixweightinput)
#print(matrixweightoutput)
#input()

for i in range(len(myresult)):
  onehotencode = myresult[i][1]
  onehotencode = onehotencode.replace(" ", "")
  onehotencode = onehotencode.replace(",", "")
  onehotencode = onehotencode.replace("[", "")
  onehotencode = onehotencode.replace("]", "")
  onehotencode = np.asarray(list(onehotencode)).astype(np.float64)
  dictionaryonehotencodekata[myresult[i][0]] = onehotencode

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
if len(katainput) != 2 :
    print("jumlah kata yang dimasukkan tidak sesuai, silahkan jalankan ulang program")
    print()
    quit()

onehotencodekata = dictionaryonehotencodekata.get(katainput[0])
onehotencodekata2 = dictionaryonehotencodekata.get(katainput[1])
#print(vectorkata)
#input()
if onehotencodekata is not None and onehotencodekata2 is not None:
  katavalid.append(katainput[0])
  katavalid.append(katainput[1])
  #print(onehotencodekata.shape)
  hiddenlayer = (1/2) * np.dot(np.transpose(matrixweightinput),(onehotencodekata + onehotencodekata2))
  uj = np.dot(np.transpose(matrixweightoutput),hiddenlayer)
  expuj = np.exp(uj - np.max(uj))
  yj = expuj/np.sum(expuj)
  #print(yj)
  #print(np.max(yj))
  #print(np.argmax(yj))
  katatengah = list(dictionaryonehotencodekata)[np.argmax(yj)]
  print("kata tengah merupakan : ", katatengah)
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
  satudua = katavalid[0] + " " + katatengah + " " + katavalid[1]
  duasatu = katavalid[1] + " " + katatengah + " " + katavalid[0]
  #print(satudua)
  #print(duasatu)
  jumlahkemunculansatudua = len(re.findall('\\b'+ satudua +'\\b',listtext[i][1]))  
  jumlahkemunculanduasatu = len(re.findall('\\b'+ duasatu +'\\b',listtext[i][1]))
  #taro [katainputvalid : jumlah kemunculan] pada dictionarykatavalidrelevan
  dictionarykatavalidrelevan[satudua] = (jumlahkemunculansatudua)
  dictionarykatavalidrelevan[duasatu] = (jumlahkemunculanduasatu)
  nilaidokumen = 1 * jumlahkemunculansatudua + 1 * jumlahkemunculanduasatu
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
  print(limadokumenpalingrelevan[i])
  #print("Hasil dokumen ranking", i+1,":", limadokumenpalingrelevan[i][0])
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))