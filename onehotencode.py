import mysql.connector
import unidecode
import time

startTime = time.time()

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
i = 0
#tuple database isinya [sumber artikel(link)][isi artikel]
while i < len(tupledatabase):

  #hapus whitespace di paragraph isi artikel kalo dia double/lebih
  #ubah data character unicode
  stringvalue = unidecode.unidecode(tupledatabase[i][1])
  stringvalue = stringvalue.lower()
  stringvalue = stringvalue.replace(",", " ")
  c =""
  for x in range(len(stringvalue)-1):
      if stringvalue[x] == " " and stringvalue[x+1] == " ":
          continue
      c = c + stringvalue[x]

  stringvalue = c
  bigdata += stringvalue
  
  #pindahin data dari database fathan + string yang udah dibersihin double/lebih whitespacenya ke database baru (tempat processing data kita)
  sql = "INSERT INTO text (sumber_url, content) VALUES (%s, %s)"
  val = (tupledatabase[i][0],stringvalue)
  targetcursor.execute(sql, val)
  targetdb.commit()
  i = i+1

print("compiling data...")
#pindahin kumpulan semua string ke table baru
sql = "INSERT INTO big_data (compiled_string) VALUES (%s)"
val = (bigdata.lower(),)
targetcursor.execute(sql, val)
targetdb.commit()

#perlu bikin biar wordnya gak duplicate dulu baru dimasukkin ke dalem database kayaknya
#terus hapus IGNORE nya
#bikin set mungkin, nanti tinggal set.add, abis itu masukkin databasenya set[x] aja gak perlu di rotasi per char lagi

print("creating unique word dictionary...")
#bikin database dictionary unique word
setkata = set()
kata = ""
jumlahKata = 0
#bigdata  = "atlético atlético atlético asdfgasgas asdfasdf 2 f2g22g2gs ssafaf "

for x in range(len(bigdata)):
  #perkarakter
  kata = kata + bigdata[x]

  #buat cek kata terakhir
  if x == len(bigdata)-1:
    kata = kata.replace(" ", "")
    setkata.add(kata)
    jumlahKata += 1
    break

  if bigdata[x] == " ":
    kata = kata.replace(" ", "")
    setkata.add(kata)
    jumlahKata += 1
    #empty-in lagi variable kata
    kata =""

#masukkin kata unique ke dalem database
#KELEMAHAN, CUMA BISA DIJALANIN SEKALI, KALO BUAT UPDATE MASUKKIN KATA UNIQUE BARU GAK BISA, KARENA DIA NGECHECK UNIQUENYA YANG SEKARANG LAGI DI PROSES DOANG KATANYA (DARI DATABASE CRAWL)
#HARUS DI CLEAR DULU DATA DICTIONARYNYA
jumlahKataUnik = 0
for x in setkata:
  jumlahKataUnik += 1
  sql = "INSERT INTO dictionary (kata) VALUES (%s)"
  val = (x,)
  targetcursor.execute(sql, val)
  targetdb.commit()

#kita gak perlu peduli ordered atau nggaknya, kita langsung input ke dalem database aja one hot encodenya
#print(len(setkata))
print("one-hot-encoding words...")
onehotencode = []
listonehotencode = []
i = 0
for x in range(len(setkata)):
  while i < len(setkata) :
    onehotencode.append(0)
    i+=1
  onehotencode[x] = 1
  #print(onehotencode)
  listonehotencode.append(onehotencode)
  i=0
  onehotencode = []
  
#print(listonehotencode)
print("saving one-hot-encode...")
#masukkin one hot encode ke database
for x in range(len(listonehotencode)):
  sql = "UPDATE dictionary SET one_hot_encode = %s WHERE id = %s"
  val = (str(listonehotencode[x]),x+1)
  targetcursor.execute(sql, val)
  targetdb.commit()


print('Jumlah Kata Tak Unik : ' + str(jumlahKata))
print('Jumlah Kata Unik : ' + str(jumlahKataUnik))
waktuJalan = (time.time() - startTime)
print('Waktu yang dibutuhkan : ' + str(waktuJalan))


#MULAI TRAINING
