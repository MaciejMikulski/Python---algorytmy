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

if usedMarkerType == "A":
    labels, images, paths = getImages(pathA)
elif usedMarkerType == "B":
    labels, images, paths = getImages(pathB)
else:
    raise Exception("Wrong marker type.")

# maximum image IDs that contain valid markers
#          Distances: 2          25         3          35         4          45         5          55
markerPresentIndex = {300.0: 40, 375.0: 80, 450.0: 79, 525.0: 80, 600.0: 80, 675.0: 80, 750.0: 80, 825.0: 80}
# Parse image labels
markerTypes, distances, imageIndexes = parseLabels(labels)


multipliers = np.arange(0.1, 2.1, 0.2)
results = []

blobAlg = blobRadiusAlg()

for k in range(len(multipliers)):
    result = []
    print("#######################################")
    for i in range(images.shape[0]):
        if i%300 == 0: print(".")
        algResult = blobAlg.blobAlgorithm(images[i,:,:], distances[i], multipliers[k])

        if imageIndexes[i] <= markerPresentIndex[distances[i]]:
            # Image contains valid marker        
            result.append(algResult)

    results.append(result)

for i in range(len(results)):
    print("############ ", multipliers[i], ":")
    for j in range(max(results[i])+1):
        print(j, ": ", results[i].count(j))
#blobRadiusAlg(logarithmic_corrected, distN)
#binary = thresholdMaxValOffset(images[N], 80)
#showImages([images[N], binary])
