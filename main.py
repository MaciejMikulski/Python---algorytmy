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
#          Distances: 2          25         3          35         4          45         5          55
markerPresentIndex = {300.0: 40, 375.0: 80, 450.0: 79, 525.0: 80, 600.0: 80, 675.0: 80, 750.0: 80, 825.0: 80}

multipliers = np.arange(1.0, 4.1, 0.3)
offsets = range(0, 100, 10)
results = []

blobAlg = blobRadiusAlg()
 
imagesNum = images.shape[0]
imagesNumDiv = imagesNum / 5
cnt = 0
for k in range(len(offsets)):
    for l in range(len(multipliers)):
        result = []
        currMultiplier = multipliers[l]
        currOffset = offsets[k]
        print("################ offset: ", currOffset, ", multiplier: ", currMultiplier, " ################")
        for i in range(imagesNum):
            if i%imagesNumDiv == 0: print(".", end="") 
            algResult = blobAlg.blobAlgorithm(images[i,:,:], distances[i], currOffset, currMultiplier)

            if imageIndexes[i] <= markerPresentIndex[distances[i]]:
                # Image contains valid marker
                cnt += 1        
                result.append(algResult)
        print(cnt)
        results.append(result)

for i in range(len(results)):
    print("############ ", offsets[i], ":")
    for j in range(max(results[i])+1):
        print(j, ": ", results[i].count(j))
#blobRadiusAlg(logarithmic_corrected, distN)
#binary = thresholdMaxValOffset(images[N], 80)
#showImages([images[N], binary])
