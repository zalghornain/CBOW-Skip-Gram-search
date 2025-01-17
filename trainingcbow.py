import numpy as np
import mysql.connector
import time
import sys

jumlahhiddenlayer = 400

learningRate = 0.05

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

#Inisiasi Weight Input (lower bound 1, higher bound 4)(aneh, lower bound di include tapi higher bound di exclude)
#W=VxN
weightinputmatrix = np.random.randint(1, 4, size=(jumlahkatadictionary, jumlahhiddenlayer))
weightinputmatrix = weightinputmatrix.astype(np.float64)

#Inisiasi Weight Output (lower bound 1, higher bound 4)
#W'=NxV
weightoutputmatrix = np.random.randint(1, 4, size=(jumlahhiddenlayer, jumlahkatadictionary))
weightoutputmatrix = weightoutputmatrix.astype(np.float64)

#ambil bigdata id paling terakhir
sourcecursor.execute("SELECT compiled_string FROM big_data WHERE ID = (SELECT MAX(ID) FROM big_data)")

rawbigdata = sourcecursor.fetchone()
bigdata = rawbigdata[0]
bigdata = bigdata.split()

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
    dictionarykata[myresult[i][0]] = np.asarray(list(onehotencodekata)).astype(np.float64)
waktuarrayonehotencode = time.time() - startTime

listdictionarykata = list(dictionarykata)

bufferweightoutput = np.empty((jumlahhiddenlayer, jumlahkatadictionary)).astype(np.float64)

#CBOW
#looping di bigdata
loop = True
iterasi = 0
while loop == True :
    listerror= np.empty((0,1),np.float64)
    print("iterasi ke : ",iterasi + 1)
    iterasi += 1
    for x in range(len(bigdata)-2):
        startTime = time.time()
        if x== 0 or x == len(bigdata)-1 :
            print("kata konteks pertama :", bigdata[x])
            print("kata ke", x+1 ," dari ", len(bigdata))
        onehotencodekatakontekssatu = dictionarykata[bigdata[x]]
        

        startTime = time.time()
        if x== 0 or x == len(bigdata)-1 :
            print("kata konteks kedua :", bigdata[x+2])
            print("kata ke", x+3 ," dari ", len(bigdata))
        onehotencodekatakonteksdua = dictionarykata[bigdata[x+2]]

        #h = (1 / jumlah kata konteks) * (W)T * sum(onehotencodeinput)  
        startTime = time.time()
        hiddenlayer = (1/2) * np.dot(np.transpose(weightinputmatrix),(onehotencodekatakontekssatu + onehotencodekatakonteksdua))

        #uj = (vwj')T * h
        startTime = time.time()
        uj = np.dot(np.transpose(weightoutputmatrix),hiddenlayer)

        startTime = time.time()
        #yj = exp(uj)/sum(exp(uj') untuk j' dari satu sampe V
        expuj = np.exp(uj - np.max(uj))
        yj = expuj/np.sum(expuj)


        #ej = yj-tj
        startTime = time.time()
        onehotencodekatatarget = dictionarykata[bigdata[x+1]]
        ej = yj - onehotencodekatatarget
        error = np.linalg.norm(yj-onehotencodekatatarget)
        listerror = np.append(listerror,np.array([[error]]),axis=0)

        #update weight matrix output
        #w'ij(new) = w'ij(old) - n.ej.hi
        startTime = time.time()
        np.multiply(learningRate, np.outer(hiddenlayer , ej, bufferweightoutput), bufferweightoutput)

        #update weight matrix input
        #vwi,c (new) = vwi,c(old) - 1/C * n * (EH)T untuk c dari 1 sampe C
        startTime = time.time()
        EH = np.dot(weightoutputmatrix,ej)
        indexkontekskatasatu = listdictionarykata.index(bigdata[x])
        indexkontekskatadua = listdictionarykata.index(bigdata[x+2])
        weightinputmatrix[indexkontekskatasatu] = weightinputmatrix[indexkontekskatasatu] - (1/2) * learningRate * np.transpose(EH)
        weightinputmatrix[indexkontekskatadua] = weightinputmatrix[indexkontekskatadua] - (1/2) * learningRate * np.transpose(EH)

        #update weight output lanjutan, ini bagian kurangin doang
        startTime = time.time()
        weightoutputmatrix -= bufferweightoutput

    ratarataerror = np.mean(listerror)
    print("rata-rata error : ", ratarataerror)
    if ratarataerror <= 0.001 or time.time() - startAwalTime >= 10800:
        loop = False


sourcedb.ping(reconnect=True)

#input weight matrix input dan output ke dalem database
startTime = time.time()
print("weight matrix input yang akan di masukkan ke database :\n", weightinputmatrix)
print()
print("weight matrix output yang akan di masukkan ke database :\n", weightoutputmatrix)
print()
sql = "INSERT INTO weight (metode, matrix_weight_input, matrix_weight_output, kata_unik, hidden_layer) VALUES (%s,%s,%s,%s,%s)"
#set threshold sebelum di simpen ke database biar gak di truncate
#supress biar dia gak di singkat jadi e-01
np.set_printoptions(threshold=sys.maxsize,suppress=True)
val = ("cbow", np.array2string(weightinputmatrix.flatten()), np.array2string(weightoutputmatrix.flatten()),jumlahkatadictionary,jumlahhiddenlayer)
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

print('Total iterasi : ' + str(iterasi))
print()

waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))