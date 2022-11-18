import numpy as np
import mysql.connector
import time
import sys

jumlahhiddenlayer = int(input("Enter number of dimension: "))

learningRate = float(input("Masukkan learning rate: "))

jumlahIterasi = int(input("Masukkan jumlah iterasi: "))

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

#Inisiasi Weight Input (lower bound 1, higher bound 4)(aneh, lower bound di include tapi higher bound di exclude)
#W=VxN
weightinputmatrix = np.random.randint(1, 4, size=(jumlahkatadictionary, jumlahhiddenlayer))
weightinputmatrix = weightinputmatrix.astype(float)
print("Weight Input Matrix :\n", weightinputmatrix)
print()

#Inisiasi Weight Output (lower bound 1, higher bound 4)
#W'=NxV
weightoutputmatrix = np.random.randint(1, 4, size=(jumlahhiddenlayer, jumlahkatadictionary))
weightoutputmatrix = weightoutputmatrix.astype(float)
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
    arrayonehotencodekata = arrayonehotencodekata.astype(float)

    dictionarykata[myresult[i][0]] = arrayonehotencodekata
waktuarrayonehotencode = time.time() - startTime

#print(dictionarykata)

totalwaktuonehotencode = 0
totalwaktuhiddenlayer = 0
totalwaktuuj = 0
totalwaktuyj = 0
totalwaktuecjplussatu = 0
totalwaktuecjminsatu = 0
totalwaktuej = 0
totalwaktuupdateweightoutput = 0
totalwaktuupdateweightinput = 0


#Skip-Gram
#looping di bigdata
for iterasi in range(jumlahIterasi):
    #print("iterasi ke : ",iterasi + 1)
    for x in range(len(bigdata)):
        startTime = time.time()
        print("kata target :", bigdata[x])
        print("kata ke", x+1 ," dari ", len(bigdata))
        onehotencode = dictionarykata[bigdata[x]]
        waktuonehotencode = time.time() - startTime
        print("one-hot encode kata target :\n", onehotencode)
        print('Waktu yang dibutuhkan untuk preprocess one hot encode string ke int : ' + str(waktuonehotencode))
        print()
        totalwaktuonehotencode += waktuonehotencode

        #hidden layer
        #h = (W)T*x
        startTime = time.time()
        #print("tipe weightinputmatrix : ", weightinputmatrix.dtype)
        #print("tipe onehotencode : ", onehotencode.dtype)
        hiddenLayer = np.matmul(np.transpose(weightinputmatrix),onehotencode)
        waktuhiddenlayer = time.time() - startTime
        print("hidden layer :\n", hiddenLayer)
        print('Waktu yang dibutuhkan untuk mendapatkan hidden layer : ' + str(waktuhiddenlayer))
        print()
        totalwaktuhiddenlayer += waktuhiddenlayer
        

        #itung ucj, hasil perkalian antara weight output matrix dengan hidden layer
        #uj = (vwj)T * h
        startTime = time.time()
        #print("tipe weightoutputmatrix : ", weightoutputmatrix.dtype)
        #print("tipe hiddenlayer : ", hiddenLayer.dtype)
        uj = np.matmul(np.transpose(weightoutputmatrix),hiddenLayer)
        waktuuj = time.time() - startTime
        print("uj:\n",uj)
        print('Waktu yang dibutuhkan untuk mendapatkan perkalian weight output dengan hidden layer : ' + str(waktuuj))
        print()
        totalwaktuuj += waktuuj


        #itung expuj
        #yj = exp(uj)/sum(exp(uj') untuk j' dari satu sampe V
        startTime = time.time()
        #shift highest value ke 0 biar gak error (nggak mempengaruhi hasil)
        expuj = np.exp(uj - np.max(uj))
        ycj = expuj/np.sum(expuj)
        #print("tipe expuj : ", expuj.dtype)
        #print("tipe ycj : ", ycj.dtype)
        waktuyj = time.time() - startTime
        print("ycj :\n", ycj)
        print('Waktu yang dibutuhkan untuk mendapatkan ycj : ' + str(waktuyj))
        print()
        totalwaktuyj += waktuyj

        ecjcplussatu = 0
        #cek one hot encode kata setelahnya
        #ecj = ycj-tcj
        if x < len(bigdata)-1:
            startTime = time.time()
            onehotencodeplussatu = dictionarykata[bigdata[x+1]]
            print("kata selanjutnya:",bigdata[x+1])
            print("one hot encode kata selanjutnya:\n", onehotencodeplussatu)
            #print('Waktu yang dibutuhkan untuk preprocess kata + 1 : ' + str(time.time() - startTime))
            #print()

            #startTime = time.time()
            ecjcplussatu = ycj - onehotencodeplussatu
            waktuecjplussatu = time.time() - startTime
            print("ecj dari c + 1:\n", ecjcplussatu)
            print('Waktu yang dibutuhkan untuk mendapatkan ecj c + 1 : ' + str(waktuecjplussatu))
            print()
            totalwaktuecjplussatu += waktuecjplussatu

        ecjcminsatu = 0
        #cek one hot encode kata sebelumnya
        #ecj = ycj-tj
        if x > 0:
            startTime = time.time()
            onehotencodeminsatu = dictionarykata[bigdata[x-1]]
            print("kata sebelumnya:",bigdata[x-1])
            print("one hot encode kata sebelumnya:\n", onehotencodeminsatu)
            #print('Waktu yang dibutuhkan untuk preprocess kata - 1 : ' + str(time.time() - startTime))
            #print()
            
            #startTime = time.time()
            ecjcminsatu = ycj - onehotencodeminsatu
            waktuecjminsatu = time.time() - startTime
            print("ecj dari c -1 :\n", ecjcminsatu)
            print('Waktu yang dibutuhkan untuk mendapatkan ecj c - 1 : ' + str(waktuecjminsatu))
            print()
            totalwaktuecjminsatu += waktuecjminsatu

        #ej = sum(ecj)
        startTime = time.time()
        ej = ecjcminsatu + ecjcplussatu
        waktuej = time.time() - startTime
        print("ej (sum dari ecj) :\n", ej)
        print('Waktu yang dibutuhkan untuk mendapatkan sum error : ' + str(waktuej))
        print()
        totalwaktuej += waktuej

        #update weight output matrix
        #W'ij(new) = W'ij(old) - n * ej * h
        #ej = sum(ecj)
        #print(np.transpose(hiddenLayer))
        startTime = time.time()
        #print("tipe hiddenlayer : ", hiddenLayer.dtype)
        #print("tipe ej : ", ej.dtype)
        bagiankanan = learningRate * np.outer(hiddenLayer , ej)
        #print("bagian kanan",bagiankanan)
        weightoutputbaru = weightoutputmatrix - bagiankanan
        waktuupdateweightoutput = time.time() - startTime
        print("updated weight output matrix:\n", weightoutputbaru)
        print('Waktu yang dibutuhkan untuk mendapatkan weight output matrix : ' + str(waktuupdateweightoutput))
        print()
        totalwaktuupdateweightoutput += waktuupdateweightoutput

        #update weight input matrix
        #Vwi(new) = Vwi(old) - n * (EH)T
        #EHi = sum (EIj * W'ij)
        #EIj = sum(ecj)
        #EH berarti perkalian matrix weight output dengan sum error yang menghasilkan N dimension vector
        #N dimension berarti dia sejumlah hidden layer
        startTime = time.time()
        #print("tipe weightoutputmatrix : ", weightoutputmatrix.dtype)
        #print("tipe ej : ", ej.dtype)
        EH = np.matmul(weightoutputmatrix,ej)
        bagiankananupdateweightinput = learningRate * np.transpose(EH)
        indexkatatarget = list(dictionarykata).index(bigdata[x])
        weightinputmatrix[indexkatatarget] = weightinputmatrix[indexkatatarget] - bagiankananupdateweightinput
        #print("jumlah dictionary kata : ", len(dictionarykata))
        #print("ukuran weight input matrix : ", weightinputmatrix.shape)
        #print("EH", EH)
        #print("EH setelah di kali learning rate", bagiankananupdateweightinput)
        #print("hidden layer", hiddenLayer)
        #print("weight input matrix", weightinputmatrix)
        #print("Vwi", Vwimatrixbaru)
        waktuupdateweightinput = time.time() - startTime
        print("updated weight input matrix:\n", weightinputmatrix)
        print('Waktu yang dibutuhkan untuk mendapatkan weight output matrix : ' + str(waktuupdateweightinput))
        print()
        totalwaktuupdateweightinput += waktuupdateweightinput
        

        #input vektor kata ke dalem databasenya setelah di update langsung
        #startTime = time.time()
        #vektorkatatarget = np.matmul(onehotencode, weightinputbaru)
        #print("kata target, one hot encode, dan vektor yang akan di update di database :\n", bigdata[x] ," ; ", onehotencode ," ; ", vektorkatatarget)
        #print()
        #sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
        #val = (str(vektorkatatarget),bigdata[x])
        #sourcecursor.execute(sql, val)
        #sourcedb.commit()
        #print('Waktu yang dibutuhkan untuk memasukkan vektor kata ke database : ' + str(time.time() - startTime))
        #print()

        
        #ganti weight output matrix lama dengan weight output matrix baru untuk kalkulasi selanjutnya
        weightoutputmatrix = weightoutputbaru

#input weight matrix input dan output ke dalem database
startTime = time.time()
print("weight matrix input yang akan di masukkan ke database :\n", weightinputmatrix)
print()
print("weight matrix output yang akan di masukkan ke database :\n", weightoutputbaru)
print()
sql = "INSERT INTO weight (metode, matrix_weight_input, matrix_weight_output) VALUES (%s, %s, %s)"
#set threshold sebelum di simpen ke database biar gak di truncate
#supress biar dia gak di singkat jadi e-01
np.set_printoptions(threshold=sys.maxsize,suppress=True)
val = ("skip-gram", np.array2string(weightinputmatrix), np.array2string(weightoutputmatrix))
sourcecursor.execute(sql, val)
sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan weight ke database : ' + str(time.time() - startTime))
print()


#input vektor kata ke dalem database setelah semua data selesai di train
#tuple berisi (vektor kata, kata)
startTime = time.time()
vektordankata = []
for x in range(jumlahkatadictionary):
    vektordankata.append((str(weightinputmatrix[x]),list(dictionarykata)[x]))

sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
val = vektordankata
sourcecursor.executemany(sql, val)
sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan vektor per kata ke database : ' + str(time.time() - startTime))
print()
print()
waktuJalan = (time.time() - startAwalTime)

print('Total waktu ubah one hot encode ke array : ' + str(waktuarrayonehotencode))
print()
print('Total waktu one hot encode : ' + str(totalwaktuonehotencode))
print()
print('Total waktu hidden layer : ' + str(totalwaktuhiddenlayer))
print()
print('Total waktu uj : ' + str(totalwaktuuj))
print()
print('Total waktu yj : ' + str(totalwaktuyj))
print()
print('Total waktu ecjplussatu : ' + str(totalwaktuecjplussatu))
print()
print('Total waktu ecjminsatu : ' + str(totalwaktuecjminsatu))
print()
print('Total waktu ej : ' + str(totalwaktuej))
print()
print('Total waktu update weight output : ' + str(totalwaktuupdateweightoutput))
print()
print('Total waktu update weight input : ' + str(totalwaktuupdateweightinput))
print()
print('Jumlah Iterasi : ' + str(jumlahIterasi))
print()
print()
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))