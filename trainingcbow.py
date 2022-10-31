from tkinter import E
import numpy as np
import mysql.connector
import time

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
i = 0
while i < jumlahkatadictionary:
    dictionarykata[myresult[i][0]] = myresult[i][1]
    i += 1

#print(dictionarykata)
#formatting one-hot encode ke array
def onehotencodestrtoarray(onehotencodeinput):
    onehotencodeinput = str(onehotencodeinput)
    #format dari [1, 0, 0, 0, 0, 0] jadi 100000 biar gampang di listnya
    onehotencodeinput = onehotencodeinput.replace(" ", "")
    onehotencodeinput = onehotencodeinput.replace(",", "")
    onehotencodeinput = onehotencodeinput.replace("[", "")
    onehotencodeinput = onehotencodeinput.replace("]", "")
    #ubah ke list biar gampang mapping ke array
    arrayonehotencodeinput = np.asarray(list(onehotencodeinput))
    arrayonehotencodeinput = arrayonehotencodeinput.astype(int)
    return arrayonehotencodeinput

#CBOW
#looping di bigdata
for x in range(len(bigdata)-2):
    startTime = time.time()
    print("kata konteks pertama :", bigdata[x])
    print("kata ke", x+1 ," dari ", len(bigdata))
    onehotencodekatakontekssatu = dictionarykata[bigdata[x]]
    arrayonehotencodekatakontekssatu = onehotencodestrtoarray(onehotencodekatakontekssatu)
    print("one-hot encode kata konteks satu :\n", arrayonehotencodekatakontekssatu)
    print('Waktu yang dibutuhkan untuk preprocess one hot encode string ke int : ' + str(time.time() - startTime))
    print()
    

    startTime = time.time()
    print("kata konteks kedua :", bigdata[x+2])
    print("kata ke", x+3 ," dari ", len(bigdata))
    onehotencodekatakonteksdua = dictionarykata[bigdata[x+2]]
    arrayonehotencodekatakonteksdua = onehotencodestrtoarray(onehotencodekatakonteksdua)
    print("one-hot encode kata konteks dua :\n", arrayonehotencodekatakonteksdua)
    print('Waktu yang dibutuhkan untuk preprocess one hot encode string ke int : ' + str(time.time() - startTime))
    print()

    #h = (1 / jumlah kata konteks) * (W)T * sum(onehotencodeinput)  
    startTime = time.time()
    hiddenlayer = (1/2) * np.dot(np.transpose(weightinputmatrix),(arrayonehotencodekatakontekssatu + arrayonehotencodekatakonteksdua))
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
    yj = []
    sumexpujaksen = 0
    for y in range(jumlahkatadictionary):
        expuj = np.exp(uj[y])
        sumexpujaksen = sumexpujaksen + expuj
        yj.append(expuj)
    yj = np.asarray(yj).astype(float)/sumexpujaksen
    print("yj :\n", yj)
    print('Waktu yang dibutuhkan untuk mendapatkan yj : ' + str(time.time() - startTime))
    print()


    #ej = yj-tj
    startTime = time.time()
    onehotencodekatatarget = dictionarykata[bigdata[x+1]]
    arrayonehotencodekatatarget = onehotencodestrtoarray(onehotencodekatatarget)
    #print(yj)
    #print(arrayonehotencodekatatarget)
    ej = yj - arrayonehotencodekatatarget
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

startTime = time.time()
for x in range(jumlahkatadictionary):
    sql = "UPDATE dictionary SET vector_cbow = %s WHERE kata = %s"
    val = (str(weightinputmatrix[x]),myresult[x][0])
    sourcecursor.execute(sql, val)
    sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan data ke database : ' + str(time.time() - startTime))
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))