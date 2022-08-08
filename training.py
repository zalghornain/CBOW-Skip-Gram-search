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

#Skip-Gram
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

    #hidden layer
    hiddenLayer = np.dot(arrayonehotencode, weightinputmatrix)
    print("hidden layer :\n", hiddenLayer)

    #itung ucj, hasil perkalian antara weight output matrix dengan hidden layer
    uj = np.dot(hiddenLayer,weightoutputmatrix)
    print("uj:\n",uj)

    y=0
    ycj = []
    #itung ycj
    for z in range(len(uj)):
        expucj = np.exp(uj[z])
        #print(uj[z])
        #print(expucj)

        sumexpuj = 0
        while y < jumlahkatadictionary:
            sumexpuj = sumexpuj + np.exp(uj[y])
            y += 1

        #print(sumexpuj)
        ycj.append(expucj/sumexpuj)
        y=0
        #print()

    ycj = np.asarray(ycj).astype(float)
    print("ycj :\n", ycj)
    print()

    ecjcplussatu = 0
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

        ecjcplussatu = ycj - arrayonehotencodeplussatu
        print("ecj dari c + 1:\n", ecjcplussatu)
        print()

    ecjcminsatu = 0
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
        
        ecjcminsatu = ycj - arrayonehotencodeminsatu
        print("ecj dari c +-1 1:\n", ecjcminsatu)
        print()

    ej = ecjcminsatu + ecjcplussatu
    print("ej (sum dari ecj) :\n", ej)
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

    #input vektor kata ke dalem databasenya setelah di update langsung
    vektorkatatarget = np.dot(arrayonehotencode, weightinputmatrix)
    print("kata target, one hot encode, dan vektor yang akan di update di database :\n", bigdata[x] ," ; ", arrayonehotencode ," ; ", vektorkatatarget)
    print()
    sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
    val = (str(vektorkatatarget),bigdata[x])
    sourcecursor.execute(sql, val)
    sourcedb.commit()

    #update weight output matrix
    #print(np.transpose(hiddenLayer))
    bagiankanan = np.dot(np.transpose(hiddenLayer).reshape(jumlahhiddenlayer,1), ej.reshape(1, jumlahkatadictionary))
    weightoutputbaru = weightoutputmatrix - (bagiankanan * learningRate)
    weightoutputmatrix = weightoutputbaru
    print("updated weight output matrix:\n", weightoutputmatrix)
    print()

#input vektor kata ke dalem database setelah semua data selesai di train
#for x in range(len(myresult)):
#    sql = "UPDATE dictionary SET vector_skip_gram = %s WHERE kata = %s"
#    val = (str(weightinputmatrix[x]),myresult[x][0])
#    sourcecursor.execute(sql, val)
#    sourcedb.commit()