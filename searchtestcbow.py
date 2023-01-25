import mysql.connector
import numpy as np
import time
import re

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
  intvektorkata = np.fromstring(myresult[i][1].strip('[').strip(']') ,sep=' ')
  dictionaryvectorkata[myresult[i][0]] = intvektorkata

startAwalTime = time.time()
dictcosinesimilarity = {}
#print(vectorkata)
listdictionaryvectorkata = list(dictionaryvectorkata)
valuesdictionarykata = list(dictionaryvectorkata.values())

sourcecursor.execute("SELECT compiled_string FROM big_data")

bigdata = sourcecursor.fetchone()
bigdata = bigdata[0]
bigdata = bigdata.split()


for x in range(len(bigdata)):
  # min 3 karena dilompatin dua dan muai dari nol
  if x == len(bigdata) - 3:
    break
  
  vectorkata = dictionaryvectorkata[bigdata[x]]
  magnitudevectorkata = np.linalg.norm(vectorkata)
  print("vector kata untuk kata", bigdata[x], "merupakan :\n", vectorkata)
  print()

  vectorkata2 = dictionaryvectorkata[bigdata[x+2]]
  magnitudevectorkata2 = np.linalg.norm(vectorkata2)
  #print(bigdata[x+2])
  #print(valuesdictionarykata[x+2])
  print("vector kata untuk kata + 2", bigdata[x+2], "merupakan :\n", vectorkata2)
  print()
  
  for y, (key, value) in enumerate(dictionaryvectorkata.items()):
    #print(key)
    #print(value)
    hasildotproduct = np.dot(vectorkata, value)
    magnitudev = np.linalg.norm(value)
    hasil = hasildotproduct / (magnitudev * magnitudevectorkata)
    #print(hasil)


    hasildotproduct2 = np.dot(vectorkata2, value)
    hasil2 = hasildotproduct2 / (magnitudev * magnitudevectorkata2)
    #print(hasil2)
    #input()
    dictcosinesimilarity[key] = (hasil + hasil2) / 2
    #print(dictcosinesimilarity[key])
    #input()

  #exclude kata input dari top five dict
  del dictcosinesimilarity[bigdata[x]]
  #misalnya kata 1 sama 3 sama udah dihapus gak perlu di hapus lagi
  if bigdata[x] != bigdata[x+2] :
    del dictcosinesimilarity[bigdata[x+2]]


  fivetopdict = sorted(dictcosinesimilarity.items(), key=lambda item: item[1], reverse=True)[0:5]
  print("5 kata paling mirip : \n",fivetopdict)
  print()
  print("tekan enter")
  #input()
  print()



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

  dokumen = None
  print(len(listtext))
  for i in range(len(listtext)):
    print("sumber ke : ", i + 1, listtext[i][0])
    print(bigdata[x])
    print(bigdata[x+2])
    #cari kata valid di kolom content dengan menggunakan regular expression
    #print(len(re.findall('\\b'+katainput+'\\b',listtext[i][1])))
    #itung jumlah kemunculan
    satudua = bigdata[x] + " " + fivetopdict[0][0] + " " + bigdata[x+2]
    duasatu = bigdata[x+2] + " " + fivetopdict[0][0] + " " + bigdata[x]
    print(satudua)
    print(duasatu)
    #harusnya * nya di hapus sebelum training
    # [
    jumlahkemunculansatudua = len(re.findall('\\b'+ satudua.replace("*","\*").replace("[","\[").replace("?","\?") +'\\b',listtext[i][1]))  
    jumlahkemunculanduasatu = len(re.findall('\\b'+ duasatu.replace("*","\*").replace("[","\[").replace("?","\?") +'\\b',listtext[i][1]))
    #taro [katainputvalid : jumlah kemunculan] pada dictionarykatavalidrelevan
    dictionarykatavalidrelevan[satudua] = (jumlahkemunculansatudua)
    dictionarykatavalidrelevan[duasatu] = (jumlahkemunculanduasatu)
    nilaidokumen = 1 * jumlahkemunculansatudua + 1 * jumlahkemunculanduasatu
    dictionarykatavalidrelevan["nilai dokumen"] = nilaidokumen
    print(nilaidokumen)

    if nilaidokumen >= 1 :
      dokumen = True
    
    print(dictionarykatavalidrelevan)
    print()
    print()
    #bikin dictionary nested [sumber : {kata input : jumlah, kata relevan : jumlah, nilai dokumen : nilai}]
    dictionarykemunculan[listtext[i][0]] = dictionarykatavalidrelevan
    dictionarykatavalidrelevan= {}

  limadokumenpalingrelevan = sorted(dictionarykemunculan.items(), key=lambda item: item[1]["nilai dokumen"], reverse=True)[0:5]
  if dokumen == True : 
    with open('hasil20persencbow.txt', 'a') as f:
      f.write('kata input : \"' + bigdata[x] + '\" , \"' + bigdata[x+2] + '\"' )
      for i in range(len(limadokumenpalingrelevan)):
        print(limadokumenpalingrelevan[i])
        f.write('\n')
        f.write(str(limadokumenpalingrelevan[i]))
      f.write('\n')
      f.write('\n')
  else : 
    for i in range(len(limadokumenpalingrelevan)):
        print(limadokumenpalingrelevan[i])

  print()
  #input()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))