from threshold import *
from helperFunctions import *
from blobRadiusAlg import *

import os
import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import silhouette_score

#usedMarkerType = "A"
usedMarkerType = "B"
#usedMarkerType = "Bcorrect"

# Path to images folder
pathA = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_A')
pathB = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_B')
pathBCorrect = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_B_poprawne')

# Path to data folder
testDataPath = os.path.join(os.path.dirname(__file__), 'CumulativeTHresholdingAreaTests', 'Marker_B')

# Get images and parsed data
if usedMarkerType == "A":
    images, markerTypes, distances, imageIndexes, filenames = getImages(pathA)
elif usedMarkerType == "B":
    images, markerTypes, distances, imageIndexes, filenames = getImages(pathB)
elif usedMarkerType == "Bcorrect":
    images, markerTypes, distances, imageIndexes, filenames = getImages(pathBCorrect)
else:
    raise Exception("Wrong marker type.")

# maximum image IDs that contain valid markers
#          Distances: 2        25        3        35        4        45        5        55
markerPresentIndex = {2.0: 40, 25.0: 80, 3.0: 79, 35.0: 80, 4.0: 80, 45.0: 80, 5.0: 80, 55.0: 80}

blobAlg = blobRadiusAlg()

areas = np.arange(370, 391, 10)
areaLowMult = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.20] 
areaLowVal = [2, 4, 6, 8, 10, 20, 30, 40, 50, 60, 70]
detectebBlobs = []
blobCounts = []
for i in range(len(areas)):    
    for j in range(len(areaLowMult)):
        print("############ area: ", areas[i], " low bound multiplier: ", areaLowMult[j], " ############", end="")
        blobNum = []
        for k in range(len(images)):
            if k % 200 == 0: print(".", end="")
            tmpBlobNum = blobAlg.blobAlgorithm(images[k], distances[k], areas[i], areaLowMult[j], "Mult")
            
            if imageIndexes[k] <= markerPresentIndex[distances[k]]:
                blobNum.append(tmpBlobNum)
        print("")
        blobNum = np.array(blobNum, dtype=int)
        detectebBlobs.append(blobNum)
        counts = np.bincount(blobNum)
        blobCounts.append(counts)
        for k in range(counts.shape[0]):
            print(k, ": ", counts[k])

for i in range(len(areas)):    
    for j in range(len(areaLowVal)):
        print("############ area: ", areas[i], " low bound value: ", areaLowVal[j], " ############", end="")
        blobNum = []
        for k in range(len(images)):
            if k % 200 == 0: print(".", end="")
            tmpBlobNum = blobAlg.blobAlgorithm(images[k], distances[k], areas[i], areaLowVal[j], "Val")
            
            if imageIndexes[k] <= markerPresentIndex[distances[k]]:
                blobNum.append(tmpBlobNum)
        print("")
        blobNum = np.array(blobNum, dtype=int)
        detectebBlobs.append(blobNum)
        counts = np.bincount(blobNum)
        blobCounts.append(counts)
        for k in range(counts.shape[0]):
            print(k, ": ", counts[k])

detectebBlobs = unevenVectorsToArray(detectebBlobs)
detectebBlobs = detectebBlobs.astype(int)
blobCounts = unevenVectorsToArray(blobCounts)
blobCounts = blobCounts.astype(int)
np.savetxt(os.path.join(testDataPath, 'Cumulative_Thres_Area_Low_Bound_raw.csv'), detectebBlobs, delimiter=',', fmt="%d")
np.savetxt(os.path.join(testDataPath, 'Cumulative_Thres_Area_Low_Bound_counts.csv'), blobCounts, delimiter=',', fmt="%d")































# angles = []
# blobNum = []
######## GET BLOB ANGLES #########
# for i in range(len(images)):
#     x, y, rot, num, blobAngles = blobAlg.blobAlgorithm(images[i], distances[i])
#     #blobNum.append(num)
#     angles.append(blobAngles)
# #print(blobNum)
# 
# angles = np.array(angles)
# angles.sort(axis=1)
# angles = np.around(angles/5.0, decimals=0)*5
# print(angles)

############### DETERMINE OPTIMAL NUMBER OF CLUSTERS ###############
#kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(angles)
#labels = kmeans.labels_

#angles0 = angles[labels == 0,:]
#angles1 = angles[labels == 1,:]
#print(angles0.shape)
#print(angles1.shape)
#print(angles.shape)
#print(angles0)
#print(angles1)

#index = []
#N = 20
#print("Davies-Bouldin scores:")
#for i in range(2,N+1,1):
#    kmeans = KMeans(n_clusters=i, random_state=0, n_init="auto").fit(angles)
#    labels = kmeans.labels_
#    score = silhouette_score(angles, labels)
#    index.append(score)
#    print("i: ", i, "score: ", score)

#for i in range(len(images)):
#    title = str(round(angles[i, 0], 3)) + " " + str(round(angles[i, 1], 3)) + " " + str(round(angles[i, 2], 3)) + " " + str(round(angles[i, 3], 3))
#    showImages([images[i,:,:]], 1, 1, title)

