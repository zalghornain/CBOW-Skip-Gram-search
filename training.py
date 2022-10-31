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



#Skip-Gram
#looping di bigdata
for x in range(len(bigdata)):
    startTime = time.time()
    print("kata target :", bigdata[x])
    print("kata ke", x+1 ," dari ", len(bigdata))
    onehotencode = dictionarykata[bigdata[x]]
    arrayonehotencode = onehotencodestrtoarray(onehotencode)
    print("one-hot encode kata target :\n", arrayonehotencode)
    print('Waktu yang dibutuhkan untuk preprocess one hot encode string ke int : ' + str(time.time() - startTime))
    print()

    #hidden layer
    #h = (W)T*x
    startTime = time.time()
    hiddenLayer = np.dot(np.transpose(weightinputmatrix),arrayonehotencode)
    print("hidden layer :\n", hiddenLayer)
    print('Waktu yang dibutuhkan untuk mendapatkan hidden layer : ' + str(time.time() - startTime))
    print()


    #itung ucj, hasil perkalian antara weight output matrix dengan hidden layer
    #uj = (vwj)T * h
    startTime = time.time()
    uj = np.dot(np.transpose(weightoutputmatrix),hiddenLayer)
    print("uj:\n",uj)
    print('Waktu yang dibutuhkan untuk mendapatkan perkalian weight output dengan hidden layer : ' + str(time.time() - startTime))
    print()


    startTime = time.time()
    ycj = []
    #itung expuj
    #yj = exp(uj)/sum(exp(uj') untuk j' dari satu sampe V
    sumexpujaksen = 0
    for y in range(jumlahkatadictionary):
        sumexpujaksen = sumexpujaksen + np.exp(uj[y])
        ycj.append(np.exp(uj[y]))
    ycj = np.asarray(ycj).astype(float)/sumexpujaksen
    print("ycj :\n", ycj)
    print('Waktu yang dibutuhkan untuk mendapatkan ycj : ' + str(time.time() - startTime))
    print()
    

    ecjcplussatu = 0
    #cek one hot encode kata setelahnya
    #ecj = ycj-tcj
    if x < len(bigdata)-1:
        startTime = time.time()
        onehotencodeplussatu = dictionarykata[bigdata[x+1]]
        print("kata selanjutnya:",bigdata[x+1])
        arrayonehotencodeplussatu = onehotencodestrtoarray(onehotencodeplussatu)
        print("one hot encode kata selanjutnya:\n", arrayonehotencodeplussatu)
        print('Waktu yang dibutuhkan untuk preprocess kata + 1 : ' + str(time.time() - startTime))
        print()

        startTime = time.time()
        ecjcplussatu = ycj - arrayonehotencodeplussatu
        print("ecj dari c + 1:\n", ecjcplussatu)
        print('Waktu yang dibutuhkan untuk mendapatkan ecj c + 1 : ' + str(time.time() - startTime))
        print()


    ecjcminsatu = 0
    #cek one hot encode kata sebelumnya
    #ecj = ycj-tj
    if x > 0:
        startTime = time.time()
        onehotencodeminsatu = dictionarykata[bigdata[x-1]]
        print("kata sebelumnya:",bigdata[x-1])
        arrayonehotencodeminsatu= onehotencodestrtoarray(onehotencodeminsatu)
        print("one hot encode kata sebelumnya:\n", arrayonehotencodeminsatu)
        print('Waktu yang dibutuhkan untuk preprocess kata - 1 : ' + str(time.time() - startTime))
        print()
        
        startTime = time.time()
        ecjcminsatu = ycj - arrayonehotencodeminsatu
        print("ecj dari c -1 :\n", ecjcminsatu)
        print('Waktu yang dibutuhkan untuk mendapatkan ecj c - 1 : ' + str(time.time() - startTime))
        print()

    startTime = time.time()
    #ej = sum(ecj)
    ej = ecjcminsatu + ecjcplussatu
    print("ej (sum dari ecj) :\n", ej)
    print('Waktu yang dibutuhkan untuk mendapatkan sum error : ' + str(time.time() - startTime))
    print()

    #update weight output matrix
    #W'ij(new) = W'ij(old) - n * ej * h
    #ej = sum(ecj)
    #print(np.transpose(hiddenLayer))
    startTime = time.time()
    bagiankanan = learningRate * np.outer(hiddenLayer , ej)
    #print("bagian kanan",bagiankanan)
    weightoutputbaru = weightoutputmatrix - bagiankanan
    print("updated weight output matrix:\n", weightoutputbaru)
    print('Waktu yang dibutuhkan untuk mendapatkan weight output matrix : ' + str(time.time() - startTime))
    print()


    #update weight input matrix
    #Vwi(new) = Vwi(old) - n * (EH)T
    #EHi = sum (EIj * W'ij)
    #EIj = sum(ecj)
    #EH berarti perkalian matrix weight output dengan sum error yang menghasilkan N dimension vector
    #N dimension berarti dia sejumlah hidden layer
    startTime = time.time()
    EH = np.dot(weightoutputmatrix,ej)
    bagiankananupdateweightinput = learningRate * np.transpose(EH)
    #bikin matrix isinya kosong semua kecuali Vwi, biar gampang nguranginnya
    Vwimatrixbaru = np.outer(arrayonehotencode, bagiankananupdateweightinput)
    #print("EH", EH)
    #print("EH setelah di kali learning rate", bagiankananupdateweightinput)
    #print("hidden layer", hiddenLayer)
    #print("weight input matrix", weightinputmatrix)
    #print("Vwi", Vwimatrixbaru)
    weightinputbaru = weightinputmatrix - Vwimatrixbaru
    print("updated weight input matrix:\n", weightinputbaru)
    print('Waktu yang dibutuhkan untuk mendapatkan weight output matrix : ' + str(time.time() - startTime))
    print()
    

    #input vektor kata ke dalem databasenya setelah di update langsung
    #startTime = time.time()
    #vektorkatatarget = np.dot(arrayonehotencode, weightinputbaru)
    #print("kata target, one hot encode, dan vektor yang akan di update di database :\n", bigdata[x] ," ; ", arrayonehotencode ," ; ", vektorkatatarget)
    #print()
    #sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
    #val = (str(vektorkatatarget),bigdata[x])
    #sourcecursor.execute(sql, val)
    #sourcedb.commit()
    #print('Waktu yang dibutuhkan untuk memasukkan vektor kata ke database : ' + str(time.time() - startTime))
    #print()

    
    #ganti weight output matrix lama dengan weight output matrix baru untuk kalkulasi selanjutnya
    weightoutputmatrix = weightoutputbaru
    weightinputmatrix = weightinputbaru

#input weight matrix input dan output ke dalem database
startTime = time.time()
print("weight matrix input yang akan di masukkan ke database :\n", weightinputbaru)
print()
print("weight matrix output yang akan di masukkan ke database :\n", weightoutputbaru)
print()
sql = "INSERT INTO weight (matrix_weight_input, matrix_weight_output) VALUES (%s,%s)"
#set threshold sebelum di simpen ke database biar gak di truncate
#supress biar dia gak di singkat jadi e-01
np.set_printoptions(threshold=sys.maxsize,suppress=True)
val = (np.array2string(weightinputmatrix),np.array2string(weightoutputmatrix))
sourcecursor.execute(sql, val)
sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan weight ke database : ' + str(time.time() - startTime))
print()


waktuJalan = (time.time() - startAwalTime)
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))

#input vektor kata ke dalem database setelah semua data selesai di train
for x in range(len(myresult)):
    sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
    val = (str(weightinputmatrix[x]),myresult[x][0])
    sourcecursor.execute(sql, val)
    sourcedb.commit()