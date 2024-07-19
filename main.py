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

usedMarkerType = "A"

# Path to images folder
pathA = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_A')
pathB = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_B')

if usedMarkerType == "A":
    labels, images, paths = getImages(pathA)
elif usedMarkerType == "B":
    labels, images, paths = getImages(pathB)
else:
    raise Exception("Wrong marker type.")




# Parse image labels
markerTypes, distances = parseLabels(labels)

print(images.shape)
print(markerTypes.shape)
print(distances.shape)

N = 800
img = images[N,:,:]
binary = thresholdCumulativeHistogramArea(images[N,:,:], distances[N])
showImages([img, binary])
#blobRadiusAlg(logarithmic_corrected, distN)
#binary = thresholdMaxValOffset(images[N], 80)
#showImages([images[N], binary])
