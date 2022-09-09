import mysql.connector
import time

startAwalTime = time.time()
startTime = startAwalTime

sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

sourcecursor = sourcedb.cursor()

#ambil data dari big_data
sourcecursor.execute("SELECT * FROM big_data")
myresult1 = sourcecursor.fetchall()
tupledatabase1 = myresult1
#print(myresult)
print('Waktu yang dibutuhkan untuk mengambil data dari big_data: ' + str(time.time() - startTime))
print()
startTime = time.time()

#ambil data dari dictionary
sourcecursor.execute("SELECT * FROM dictionary")
myresult2 = sourcecursor.fetchall()
tupledatabase2 = myresult2
#print(myresult)
print('Waktu yang dibutuhkan untuk mengambil data dari dictionary: ' + str(time.time() - startTime))
print()
startTime = time.time()

#ambil data dari text
sourcecursor.execute("SELECT * FROM text")
myresult3 = sourcecursor.fetchall()
tupledatabase3 = myresult3
#print(myresult)
print('Waktu yang dibutuhkan untuk mengambil data dari text: ' + str(time.time() - startTime))
print()
startTime = time.time()


with open("big_data.txt", "a") as f:
  print(tupledatabase1, file=f)

with open("dictionary.txt", "a") as f:
  print(tupledatabase2, file=f)

with open("text.txt", "a") as f:
  print(tupledatabase3, file=f)

print('Waktu yang dibutuhkan untuk print text: ' + str(time.time() - startTime))
print()
startTime = time.time()


waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))
print()
input("Please press the Enter key to proceed")