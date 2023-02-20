import random
import mysql.connector
import unidecode
import time
import re

startAwalTime = time.time()
startTime = startAwalTime

sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="dbcrawl"
)

sourcecursor = sourcedb.cursor()

#ambil data dari dbcrawl, hasil tools fathan
sourcecursor.execute("SELECT base_url,content_text FROM page_information")

myresult = sourcecursor.fetchall()

tupledatabase = myresult

targetdb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

targetcursor = targetdb.cursor()

#inisiasi string kosong untuk campuran semua string nanti
bigdata = ""

#list index dokumen yang udah dipilih
sampledDokumen = []

#stopwords
with open('stopwords.txt', 'r') as file:
    stopwords = file.read().split()

print("cleaning double whitespace...")
#tuple database isinya [sumber artikel(link)][isi artikel]
for iterasi in range(70):

  x = random.randint(0, len(tupledatabase)-1)
  while x in sampledDokumen :
    x = random.randint(0, len(tupledatabase)-1)
  sampledDokumen.append(x)
  
  #ubah data character unicode
  stringvalue = unidecode.unidecode(tupledatabase[x][1])
  stringvalue = stringvalue.lower()
  stringvalue = stringvalue.replace(",", " ")
  stringvalue = stringvalue.replace(".", " ")
  stringvalue = stringvalue.replace("\""," ")
  stringvalue = stringvalue.replace("#"," ")
  stringvalue = stringvalue.replace("&"," ")
  stringvalue = stringvalue.replace("'","")
  stringvalue = stringvalue.replace("("," ")
  stringvalue = stringvalue.replace(")"," ")
  stringvalue = stringvalue.replace("@"," ")
  stringvalue = stringvalue.replace("/"," ")
  stringvalue = stringvalue.replace(":"," ")
  stringvalue = stringvalue.replace("*"," ")
  stringvalue = stringvalue.replace("["," ")
  stringvalue = stringvalue.replace("]"," ")
  stringvalue = stringvalue.replace("?"," ")
  stringvalue = stringvalue.replace("-"," ")
  stringvalue = stringvalue.replace("%"," ")
  stringvalue = stringvalue.replace("$"," ")
  stringvalue = stringvalue.replace("!"," ")
  stringvalue = stringvalue.replace("<"," ")
  stringvalue = stringvalue.replace(">"," ")
  stringvalue = stringvalue.replace("="," ")
  stringvalue = stringvalue.replace("|"," ")
  stringvalue = stringvalue.replace("_"," ")
  stringvalue = stringvalue.replace(";"," ")

  #hapus stopwords
  for nomor in range(len(stopwords)) :
    stringvalue = re.sub('\\b'+stopwords[nomor]+'\\b', '', stringvalue)

  stringvaluesplit = stringvalue.split()
  realstringvalue = []
  #hapus kata yang isinya number doang
  for z in range(len(stringvaluesplit)) :
    if stringvaluesplit[z].isdigit() == False:
      realstringvalue.append(stringvaluesplit[z])

  #hapus whitespace di paragraph isi artikel kalo dia double/lebih
  stringvalue = ' '.join(realstringvalue)
  
  bigdata += stringvalue
  
  #pindahin data dari database fathan + string yang udah dibersihin double/lebih whitespacenya ke database baru (tempat processing data kita)
  sql = "INSERT INTO text (sumber_url, content) VALUES (%s, %s)"
  val = (tupledatabase[x][0],stringvalue)
  targetcursor.execute(sql, val)
  targetdb.commit()
print('jumlah data : ' + str(len(tupledatabase)))
print('Waktu yang dibutuhkan : ' + str(time.time() - startTime))
print()
startTime = time.time()

print("compiling data...")
#pindahin kumpulan semua string ke table baru
sql = "INSERT INTO big_data (compiled_string) VALUES (%s)"
val = (bigdata,)
targetcursor.execute(sql, val)
targetdb.commit()
print('Waktu yang dibutuhkan : ' + str(time.time() - startTime))
print()
startTime = time.time()

#perlu bikin biar wordnya gak duplicate dulu baru dimasukkin ke dalem database kayaknya
print("creating unique word dictionary...")
#bikin database dictionary unique word
listKata = bigdata.split()
listKata.sort()
listKataUnik = list(dict.fromkeys(listKata))
print('Jumlah Kata Tak Unik : ' + str(len(listKata)))
print('Jumlah Kata Unik : ' + str(len(listKataUnik)))
print('Waktu yang dibutuhkan : ' + str(time.time() - startTime))
print()
startTime = time.time()

#tuple berisi (kataUnik, one_hot_encode)
kataUnikDanOneHotEncode = []
#kita gak perlu peduli ordered atau nggaknya, one hot encode + kata langsung di ram
print("one-hot-encoding words...")
onehotencode = []
i = 0
for x in range(len(listKataUnik)):
  while i < len(listKataUnik) :
    onehotencode.append(0)
    i+=1
  onehotencode[x] = 1
  kataUnikDanOneHotEncode.append((listKataUnik[x], str(onehotencode)))
  i=0
  onehotencode = []
print('Waktu yang dibutuhkan : ' + str(time.time() - startTime))
print()
startTime = time.time()

print("saving unique word to database...")
#masukkin kata unique ke dalem database
sql = "INSERT INTO dictionary (kata , one_hot_encode) VALUES (%s, %s)"
val = kataUnikDanOneHotEncode
targetcursor.executemany(sql, val)
targetdb.commit()
print('Waktu yang dibutuhkan : ' + str(time.time() - startTime))
print()
startTime = time.time()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))


#MULAI TRAINING
