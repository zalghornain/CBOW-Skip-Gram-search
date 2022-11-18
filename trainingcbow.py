from tkinter import E
import numpy as np
import mysql.connector
import time
import sys

startAwalTime = time.time()

sourcedb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="skripsi"
)

sourcecursor = sourcedb.cursor()

#ambil data dari dbcrawl, hasil tools fathan
sourcecursor.execute("SELECT kata,one_hot_encode FROM dictionary")

myresult = sourcecursor.fetchall()
jumlahkatadictionary = sourcecursor.rowcount

#print(myresult)

print("Jumlah Kata Unik :", jumlahkatadictionary)
jumlahhiddenlayer = int(input("Enter number of dimension: "))

learningRate = float(input("Masukkan learning rate: "))

jumlahIterasi = int(input("Masukkan jumlah iterasi: "))

#Inisiasi Weight Input (lower bound 1, higher bound 4)(aneh, lower bound di include tapi higher bound di exclude)
#W=VxN
weightinputmatrix = np.random.randint(1, 4, size=(jumlahkatadictionary, jumlahhiddenlayer))
print("Weight Input Matrix :\n", weightinputmatrix)
print()

#Inisiasi Weight Output (lower bound 1, higher bound 4)
#W'=NxV
weightoutputmatrix = np.random.randint(1, 4, size=(jumlahhiddenlayer, jumlahkatadictionary))
print("Weight Output Matrix :\n", weightoutputmatrix)
print()

#ambil bigdata id paling terakhir
sourcecursor.execute("SELECT compiled_string FROM big_data WHERE ID = (SELECT MAX(ID) FROM big_data)")

rawbigdata = sourcecursor.fetchone()
bigdata = rawbigdata[0]
bigdata = bigdata.split()
print("corpus :",bigdata)
print()
#print(myresult[0][0])

#print(jumlahkatadictionary)

dictionarykata = {}
#bikin dictionary kata dan one hot encode
startTime = time.time()
for i in range(jumlahkatadictionary):
    #ubah semua one hot encode ke array
    onehotencodekata = str(myresult[i][1])
    #format dari [1, 0, 0, 0, 0, 0] jadi 100000 biar gampang di listnya
    onehotencodekata = onehotencodekata.replace(" ", "")
    onehotencodekata = onehotencodekata.replace(",", "")
    onehotencodekata = onehotencodekata.replace("[", "")
    onehotencodekata = onehotencodekata.replace("]", "")
    #ubah ke list biar gampang mapping ke array
    arrayonehotencodekata = np.asarray(list(onehotencodekata))
    arrayonehotencodekata = arrayonehotencodekata.astype(int)

    dictionarykata[myresult[i][0]] = arrayonehotencodekata
waktuarrayonehotencode = time.time() - startTime

#print(dictionarykata)

#CBOW
#looping di bigdata
for iterasi in range(jumlahIterasi):
    print("iterasi ke : ",iterasi + 1)
    for x in range(len(bigdata)-2):
        startTime = time.time()
        print("kata konteks pertama :", bigdata[x])
        print("kata ke", x+1 ," dari ", len(bigdata))
        onehotencodekatakontekssatu = dictionarykata[bigdata[x]]
        print("one-hot encode kata konteks satu :\n", onehotencodekatakontekssatu)
        print('Waktu yang dibutuhkan untuk preprocess one hot encode string ke int : ' + str(time.time() - startTime))
        print()
        

        startTime = time.time()
        print("kata konteks kedua :", bigdata[x+2])
        print("kata ke", x+3 ," dari ", len(bigdata))
        onehotencodekatakonteksdua = dictionarykata[bigdata[x+2]]
        print("one-hot encode kata konteks dua :\n", onehotencodekatakonteksdua)
        print('Waktu yang dibutuhkan untuk preprocess one hot encode string ke int : ' + str(time.time() - startTime))
        print()

        #h = (1 / jumlah kata konteks) * (W)T * sum(onehotencodeinput)  
        startTime = time.time()
        hiddenlayer = (1/2) * np.dot(np.transpose(weightinputmatrix),(onehotencodekatakontekssatu + onehotencodekatakonteksdua))
        print("hidden layer :\n", hiddenlayer)
        print('Waktu yang dibutuhkan untuk mendapatkan hidden layer : ' + str(time.time() - startTime))
        print()

        #uj = (vwj')T * h
        startTime = time.time()
        uj = np.dot(np.transpose(weightoutputmatrix),hiddenlayer)
        print("uj:\n",uj)
        print('Waktu yang dibutuhkan untuk mendapatkan perkalian weight output dengan hidden layer : ' + str(time.time() - startTime))
        print()

        startTime = time.time()
        #yj = exp(uj)/sum(exp(uj') untuk j' dari satu sampe V
        expuj = np.exp(uj)
        yj = expuj/np.sum(expuj)
        print("yj :\n", yj)
        print('Waktu yang dibutuhkan untuk mendapatkan yj : ' + str(time.time() - startTime))
        print()


        #ej = yj-tj
        startTime = time.time()
        onehotencodekatatarget = dictionarykata[bigdata[x+1]]
        #print(yj)
        #print(arrayonehotencodekatatarget)
        ej = yj - onehotencodekatatarget
        print("ej :\n", ej)
        print('Waktu yang dibutuhkan untuk mendapatkan ej : ' + str(time.time() - startTime))
        print()

        #update weight matrix output
        #w'ij(new) = w'ij(old) - n.ej.hi
        #print(ej)
        startTime = time.time()
        weightoutputmatrixbaru = weightoutputmatrix - learningRate * np.outer(hiddenlayer,ej)
        print("updated weight output matrix:\n", weightoutputmatrixbaru)
        print('Waktu yang dibutuhkan untuk mendapatkan weight output matrix : ' + str(time.time() - startTime))
        print()
        #print(weightoutputmatrix)
        #print(weightoutputmatrixbaru)

        #update weight matrix input
        #vwi,c (new) = vwi,c(old) - 1/C * n * (EH)T untuk c dari 1 sampe C
        startTime = time.time()
        EH = np.dot(weightoutputmatrix,ej)
        #print("weight input matrix c1:\n", weightinputmatrix[x])
        #print("weight input matrix c2:\n", weightinputmatrix[x+2])
        weightinputmatrix = np.asarray(weightinputmatrix).astype(float)
        #print(weightinputmatrix[x])
        #print((1/2) * learningRate * np.transpose(EH))
        indexkontekskatasatu = list(dictionarykata).index(bigdata[x])
        indexkontekskatadua = list(dictionarykata).index(bigdata[x+2])
        weightinputmatrix[indexkontekskatasatu] = weightinputmatrix[indexkontekskatasatu] - (1/2) * learningRate * np.transpose(EH)
        weightinputmatrix[indexkontekskatadua] = weightinputmatrix[indexkontekskatadua] - (1/2) * learningRate * np.transpose(EH)
        print("updated weight input matrix:\n", weightinputmatrix)
        print('Waktu yang dibutuhkan untuk mendapatkan weight output matrix : ' + str(time.time() - startTime))
        print()
        #print("weight input matrix baru c1:\n", vwickonteksdua)
        #print("weight input matrix baru c2:\n", vwickonteksdua)

        #ganti weight output matrix lama dengan weight output matrix baru untuk kalkulasi selanjutnya
        weightoutputmatrix = weightoutputmatrixbaru


#input weight matrix input dan output ke dalem database
startTime = time.time()
print("weight matrix input yang akan di masukkan ke database :\n", weightinputmatrix)
print()
print("weight matrix output yang akan di masukkan ke database :\n", weightoutputmatrix)
print()
sql = "INSERT INTO weight (metode, matrix_weight_input, matrix_weight_output) VALUES (%s,%s,%s)"
#set threshold sebelum di simpen ke database biar gak di truncate
#supress biar dia gak di singkat jadi e-01
np.set_printoptions(threshold=sys.maxsize,suppress=True)
val = ("cbow", np.array2string(weightinputmatrix), np.array2string(weightoutputmatrix))
sourcecursor.execute(sql, val)
sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan weight ke database : ' + str(time.time() - startTime))
print()


#input vektor kata ke dalem database setelah semua data selesai di train
#tuple berisi (vektor kata, kata)
startTime = time.time()
vektordankata = []
for x in range(jumlahkatadictionary):
    vektordankata.append((str(weightinputmatrix[x]),myresult[x][0]))

sql = "UPDATE dictionary SET vector_cbow = %s WHERE kata = %s"
val = vektordankata
sourcecursor.executemany(sql, val)
sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan vektor per kata ke database : ' + str(time.time() - startTime))
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))