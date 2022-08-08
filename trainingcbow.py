import numpy as np
import mysql.connector

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
weightinputmatrix = np.random.randint(1, 4, size=(jumlahkatadictionary, jumlahhiddenlayer))
print("Weight Input Matrix :\n", weightinputmatrix)
print()

#Inisiasi Weight Output (lower bound 1, higher bound 4)
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

#CBOW
#looping di bigdata
for x in range(len(bigdata)):
    print("kata target :", bigdata[x])
    print("kata ke", x+1 ," dari ", len(bigdata))
    onehotencode = dictionarykata[bigdata[x]]
    #formatting one-hot encode ke array
    onehotencode = str(onehotencode)
    #format dari [1, 0, 0, 0, 0, 0] jadi 100000 biar gampang di listnya
    onehotencode = onehotencode.replace(" ", "")
    onehotencode = onehotencode.replace(",", "")
    onehotencode = onehotencode.replace("[", "")
    onehotencode = onehotencode.replace("]", "")
    #ubah ke list biar gampang mapping ke array
    onehotencode = list(onehotencode)

    arrayonehotencode = np.asarray(list(onehotencode))
    arrayonehotencode = arrayonehotencode.astype(int)
    print("one-hot encode kata target :\n", arrayonehotencode)

    
    #cek one hot encode kata setelahnya
    if x < len(bigdata)-1:
        onehotencodeplussatu = dictionarykata[bigdata[x+1]]
        print("kata selanjutnya:",bigdata[x+1])
        #formatting one-hot encode ke array
        onehotencodeplussatu = str(onehotencodeplussatu)
        #format dari [1, 0, 0, 0, 0, 0] jadi 100000 biar gampang di listnya
        onehotencodeplussatu = onehotencodeplussatu.replace(" ", "")
        onehotencodeplussatu = onehotencodeplussatu.replace(",", "")
        onehotencodeplussatu = onehotencodeplussatu.replace("[", "")
        onehotencodeplussatu = onehotencodeplussatu.replace("]", "")
        #ubah ke list biar gampang mapping ke array
        onehotencodeplussatu = list(onehotencodeplussatu)

        arrayonehotencodeplussatu = np.asarray(list(onehotencodeplussatu))
        arrayonehotencodeplussatu = arrayonehotencodeplussatu.astype(int)
        print("one hot encode kata selanjutnya:\n", arrayonehotencodeplussatu)
        print()

    #cek one hot encode kata sebelumnya
    if x > 0:
        onehotencodeminsatu = dictionarykata[bigdata[x-1]]
        print("kata sebelumnya:",bigdata[x-1])
        #formatting one-hot encode ke array
        onehotencodeminsatu = str(onehotencodeminsatu)
        #format dari [1, 0, 0, 0, 0, 0] jadi 100000 biar gampang di listnya
        onehotencodeminsatu = onehotencodeminsatu.replace(" ", "")
        onehotencodeminsatu = onehotencodeminsatu.replace(",", "")
        onehotencodeminsatu = onehotencodeminsatu.replace("[", "")
        onehotencodeminsatu = onehotencodeminsatu.replace("]", "")
        #ubah ke list biar gampang mapping ke array
        onehotencodeminsatu = list(onehotencodeminsatu)

        arrayonehotencodeminsatu = np.asarray(list(onehotencodeminsatu))
        arrayonehotencodeminsatu = arrayonehotencodeminsatu.astype(int)
        print("one hot encode kata sebelumnya:\n", arrayonehotencodeminsatu)
        print()

    C=0
    #rata-ratain one hot encode kata input
    if x == len(bigdata)-1:
        #ini terakhir, berarti gak ada kata setelah
        C=2
        arrayAvgOneHotEncode = (arrayonehotencodeminsatu + arrayonehotencode)/C
        print("rata-rata one hot encodenya : \n",arrayAvgOneHotEncode)
        print()
    elif x == 0 :
        #ini pertama, berarti gak ada kata sebelum
        C=2
        arrayAvgOneHotEncode = (arrayonehotencodeplussatu + arrayonehotencode)/C
        print("rata-rata one hot encodenya : \n",arrayAvgOneHotEncode)
        print()
    else :
        #ini selain itu, berarti tiga tiganya
        C=3
        arrayAvgOneHotEncode = (arrayonehotencodeplussatu + arrayonehotencode + arrayonehotencodeminsatu)/C
        print("rata-rata one hot encodenya : \n",arrayAvgOneHotEncode)
        print()

    #hidden layer
    hiddenLayer = np.dot(arrayAvgOneHotEncode, weightinputmatrix)
    print("hidden layer :\n", hiddenLayer)

    #itung uj, hasil perkalian antara weight output matrix dengan hidden layer
    uj = np.dot(hiddenLayer,weightoutputmatrix)
    print("uj:\n",uj)

    y=0
    yj = []
    #itung yj
    for z in range(len(uj)):
        expuj = np.exp(uj[z])
        #print(uj[z])
        #print(expucj)

        sumexpuj = 0
        while y < jumlahkatadictionary:
            sumexpuj = sumexpuj + np.exp(uj[y])
            y += 1

        #print(sumexpuj)
        yj.append(expuj/sumexpuj)
        y=0
        #print()

    yj = np.asarray(yj).astype(float)
    print("ycj :\n", yj)
    print()

    ej = yj - arrayonehotencode
    print("ej (error kata target) :\n", ej)
    print()

    #update weight output matrix
    bagiankanan = np.dot(np.transpose(hiddenLayer).reshape(jumlahhiddenlayer,1), ej.reshape(1, jumlahkatadictionary))
    weightoutputbaru = weightoutputmatrix - (bagiankanan * learningRate)
    weightoutputmatrix = weightoutputbaru
    print("updated weight output matrix:\n", weightoutputmatrix)
    print()

    #update weight input matrix
    EH = np.dot(np.transpose(ej).reshape(1,jumlahkatadictionary),weightoutputmatrix.reshape(jumlahkatadictionary,jumlahhiddenlayer))
    bagiankananupdateweightinput = learningRate * EH
    #print("bagian kanan update weight input: \n",bagiankananupdateweightinput)
    #print()
    print("weight input matrix lama \n", weightinputmatrix)
    print()
    weightinputmatrixbaru = np.dot(arrayonehotencode.reshape(jumlahkatadictionary,1), bagiankananupdateweightinput)
    print("weight input matrix baru \n", weightinputmatrixbaru)
    print()
    weightinputmatrix = weightinputmatrix - weightinputmatrixbaru
    print("updated weight input matrix :\n", weightinputmatrix)
    print()

