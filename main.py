from threshold import *
from helperFunctions import *
from blobRadiusAlg import *

import skimage as ski
from skimage.io import imshow
from skimage import exposure
from skimage.filters import try_all_threshold


import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from skimage import data, img_as_float
from skimage import exposure

usedMarkerType = "B"

# Path to images folder
pathA = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_A')
pathB = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_B')

# Get images and parsed data
if usedMarkerType == "A":
    images, markerTypes, distances, imageIndexes, paths = getImages(pathA)
elif usedMarkerType == "B":
    images, markerTypes, distances, imageIndexes, paths = getImages(pathB)
else:
    raise Exception("Wrong marker type.")

# maximum image IDs that contain valid markers
#          Distances: 2        25        3        35        4        45        5        55
markerPresentIndex = {2.0: 40, 25.0: 80, 3.0: 79, 35.0: 80, 4.0: 80, 45.0: 80, 5.0: 80, 55.0: 80}

multipliers = np.arange(0.0, 4.1, 0.25)
offsets = range(0, 50, 10)
results = []

blobAlg = blobRadiusAlg()

imagesNum = images.shape[0]
resultImages = np.zeros((imagesNum, 120, 160))
for k in range(len(offsets)):
    for l in range(len(multipliers)):
        result = []
        currMultiplier = multipliers[l]
        currOffset = offsets[k]
        print("################ offset: ", currOffset, ", multiplier: ", currMultiplier, " ################")
        for i in range(imagesNum):
            if i % 200 == 0: print(".", end="") 
            resultImage, algResult = blobAlg.blobAlgorithm(images[i,:,:], distances[i], currOffset, currMultiplier)

            resultImages[i,:,:] = resultImage
            if imageIndexes[i] <= markerPresentIndex[distances[i]]:
                # Image contains valid marker        
                result.append(algResult)
        results.append(result)

for k in range(len(offsets)):
    for l in range(len(multipliers)):
        print("################ offset: ", offsets[k], ", multiplier: ", multipliers[l], " ################")
        for j in range(max(results[k*len(offsets)+l])+1):
            print(j, ": ", results[k*len(offsets)+l].count(j))


#blobRadiusAlg(logarithmic_corrected, distN)
#binary = thresholdMaxValOffset(images[N], 80)
#showImages([images[N], binary])
