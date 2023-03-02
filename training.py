import numpy as np
import mysql.connector
import time
import sys

jumlahhiddenlayer = 400

learningRate = 0.7

jumlahIterasi = 1000

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
print("Weight Input Matrix :\n", weightinputmatrix)

#Inisiasi Weight Output (lower bound 1, higher bound 4)
#W'=NxV
weightoutputmatrix = np.random.randint(1, 4, size=(jumlahhiddenlayer, jumlahkatadictionary))
weightoutputmatrix = weightoutputmatrix.astype(np.float64)
print("Weight Output Matrix :\n", weightoutputmatrix)

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


totalwaktuonehotencode = 0
totalwaktuhiddenlayer = 0
totalwaktuuj = 0
totalwaktuyj = 0
totalwaktuecjplussatu = 0
totalwaktuecjminsatu = 0
totalwaktuej = 0
totalwaktuperkalianweightoutput = 0
totalwaktupenguranganweightoutput = 0
totalwaktuupdateweightinput = 0
listdictionarykata = list(dictionarykata)

bufferweightoutput = np.empty((jumlahhiddenlayer, jumlahkatadictionary)).astype(np.float64)

#Skip-Gram
#looping di bigdata
loop = True
iterasi = 0
while loop == True:
    iterasi = iterasi + 1
    listerror= np.empty((0,1),np.float64)
    listerrorminsatu= np.empty((0,1),np.float64)
    listerrorplussatu= np.empty((0,1),np.float64)
    print("iterasi ke : ",iterasi)
    for x in range(len(bigdata)):
        startTime = time.time()
        if x== 0 or x == len(bigdata)-1 :
            print("kata ke", x+1 ," dari ", len(bigdata))
        onehotencodekatatarget = dictionarykata[bigdata[x]]
        waktuonehotencode = time.time() - startTime
        totalwaktuonehotencode += waktuonehotencode

        #hidden layer
        #h = (W)T*x
        startTime = time.time()
        hiddenLayer = np.dot(np.transpose(weightinputmatrix),onehotencodekatatarget)
        waktuhiddenlayer = time.time() - startTime
        totalwaktuhiddenlayer += waktuhiddenlayer

        #itung ucj, hasil perkalian antara weight output matrix dengan hidden layer
        #uj = (vwj)T * h
        startTime = time.time()
        uj = np.dot(np.transpose(weightoutputmatrix),hiddenLayer)
        waktuuj = time.time() - startTime
        totalwaktuuj += waktuuj

        #itung expuj
        #yj = exp(uj)/sum(exp(uj') untuk j' dari satu sampe V
        startTime = time.time()
        #shift highest value ke 0 biar gak error (nggak mempengaruhi hasil)
        expuj = np.exp(uj - np.max(uj))
        ycj = expuj/np.sum(expuj)
        waktuyj = time.time() - startTime
        totalwaktuyj += waktuyj

        ecjcplussatu = 0
        errorplussatu = 0
        #cek one hot encode kata setelahnya
        #ecj = ycj-tcj
        if x < len(bigdata)-1:
            startTime = time.time()
            onehotencodeplussatu = dictionarykata[bigdata[x+1]]
            ecjcplussatu = ycj - onehotencodeplussatu
            waktuecjplussatu = time.time() - startTime
            totalwaktuecjplussatu += waktuecjplussatu

        ecjcminsatu = 0
        errorminsatu = 0
        #cek one hot encode kata sebelumnya
        #ecj = ycj-tj
        if x > 0 :
            startTime = time.time()
            onehotencodeminsatu = dictionarykata[bigdata[x-1]]
            ecjcminsatu = ycj - onehotencodeminsatu
            waktuecjminsatu = time.time() - startTime
            totalwaktuecjminsatu += waktuecjminsatu

        #ej = sum(ecj)
        startTime = time.time()
        ej = ecjcminsatu + ecjcplussatu
        waktuej = time.time() - startTime
        if x > 0 and x < len(bigdata)-1:
            errorplus = np.linalg.norm(ycj-onehotencodeplussatu)
            errormin = np.linalg.norm(ycj-onehotencodeminsatu)
            totalerror = errorplus + errormin
            listerrorminsatu = np.append(listerrorminsatu,np.array([[errormin]]),axis=0) 
            listerrorplussatu = np.append(listerrorplussatu,np.array([[errorplus]]),axis=0)
            c = 2
            error = -(c * uj) + c * np.log(np.sum(expuj))
        elif x == len(bigdata)-1 :
            totalerror = np.linalg.norm(ycj-onehotencodeminsatu)
            errormin = np.linalg.norm(ycj-onehotencodeminsatu)
            listerrorminsatu = np.append(listerrorminsatu,np.array([[errormin]]),axis=0)
            c = 1
            error = -(c * uj) + c * np.log(np.sum(expuj))
        elif x == 0 :
            totalerror = np.linalg.norm(ycj-onehotencodeplussatu)
            errorplus = np.linalg.norm(ycj-onehotencodeplussatu)
            listerrorplussatu = np.append(listerrorplussatu,np.array([[errorplus]]),axis=0)
            c = 1
            error = -(c * uj) + (c * np.log(np.sum(expuj)))
        listerror = np.append(listerror,np.array([[totalerror]]),axis=0)

        totalwaktuej += waktuej

        #update weight output matrix
        #W'ij(new) = W'ij(old) - n * ej * h
        #ej = sum(ecj)
        startTime = time.time()
        #pakai buffer buat multiply dan outer, biar cepet
        np.multiply(learningRate, np.outer(hiddenLayer , ej, bufferweightoutput), bufferweightoutput)
        waktuperkalianweightoutput = time.time() - startTime
        totalwaktuperkalianweightoutput += waktuperkalianweightoutput

        #update weight input matrix
        #Vwi(new) = Vwi(old) - n * (EH)T
        #EHi = sum (EIj * W'ij)
        #EIj = sum(ecj)
        #EH berarti perkalian matrix weight output dengan sum error yang menghasilkan N dimension vector
        #N dimension berarti dia sejumlah hidden layer
        startTime = time.time()
        EH = np.dot(weightoutputmatrix,ej)
        indexkatatarget = listdictionarykata.index(bigdata[x])
        weightinputmatrix[indexkatatarget] = weightinputmatrix[indexkatatarget] - learningRate * np.transpose(EH)
        waktuupdateweightinput = time.time() - startTime
        totalwaktuupdateweightinput += waktuupdateweightinput

        #update weight output lanjutan, ini bagian kurangin doang
        startTime = time.time()
        weightoutputmatrix -= bufferweightoutput
        waktupenguranganweightoutput = time.time() - startTime
        totalwaktupenguranganweightoutput += waktupenguranganweightoutput

        
    
    ratarataerrorminsatu = np.mean(listerrorminsatu)
    ratarataerrorplussatu = np.mean(listerrorplussatu)
    ratarataerror = np.mean(listerror)
    print("rata-rata error : ", ratarataerror)
    print("error : ", error)
    print("rata-rata error min satu : ", ratarataerrorminsatu)
    print("rata-rata error plus satu : ", ratarataerrorplussatu)
    if time.time() - startAwalTime >= 10800:
        loop = False
      
      
sourcedb.ping(reconnect=True)

#input weight matrix input dan output ke dalem database
startTime = time.time()
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
    vektordankata.append((str(weightinputmatrix[x]),listdictionarykata[x]))

sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
val = vektordankata
sourcecursor.executemany(sql, val)
sourcedb.commit()
print('Waktu yang dibutuhkan untuk memasukkan vektor per kata ke database: ' + str(time.time() - startTime))
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
print('Total waktu perkalian weight output : ' + str(totalwaktuperkalianweightoutput))
print()
print('Total waktu pengurangan weight output : ' + str(totalwaktupenguranganweightoutput))
print()
print('Total waktu update weight input : ' + str(totalwaktuupdateweightinput))
print()
print('Jumlah Iterasi : ' + str(iterasi))
print()
print()
print('Waktu total yang dibutuhkan : ' + str(waktuJalan))