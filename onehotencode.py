import mysql.connector
import unidecode
import time

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

print("cleaning double whitespace...")
#tuple database isinya [sumber artikel(link)][isi artikel]
for x in range(len(tupledatabase)):

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
  #hapus whitespace di paragraph isi artikel kalo dia double/lebih
  stringvalue = ' '.join(stringvalue.split())
  bigdata += stringvalue
  
  #pindahin data dari database fathan + string yang udah dibersihin double/lebih whitespacenya ke database baru (tempat processing data kita)
  sql = "INSERT INTO text (sumber_url, content) VALUES (%s, %s)"
  val = (tupledatabase[x][0],stringvalue)
  targetcursor.execute(sql, val)
  targetdb.commit()
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
#bigdata  = "saya sedang bermain budi sedang makan "
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
#print(len(setkata))
print("one-hot-encoding words...")
onehotencode = []
i = 0
for x in range(len(listKataUnik)):
  while i < len(listKataUnik) :
    onehotencode.append(0)
    i+=1
  onehotencode[x] = 1
  #print(onehotencode)
  kataUnikDanOneHotEncode.append((listKataUnik[x], str(onehotencode)))
  i=0
  onehotencode = []
print('Waktu yang dibutuhkan : ' + str(time.time() - startTime))
print()
startTime = time.time()

print("saving unique word to database...")
#masukkin kata unique ke dalem database
#KELEMAHAN, CUMA BISA DIJALANIN SEKALI, KALO BUAT UPDATE MASUKKIN KATA UNIQUE BARU GAK BISA, KARENA DIA NGECHECK UNIQUENYA YANG SEKARANG LAGI DI PROSES DOANG KATANYA (DARI DATABASE CRAWL)
#HARUS DI CLEAR DULU DATA DICTIONARYNYA
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
