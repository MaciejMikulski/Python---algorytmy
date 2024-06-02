from threshold import *
from helperFunctions import *
from blobRadiusAlg import *

import skimage as ski
from skimage.io import imshow
from skimage import exposure
from skimage.filters import try_all_threshold


# Path to images folder
path = "Zdjecia/Testowy_marker"
# Get all image names
labels, images, paths = getImages(path)
# Parse image names
markerTypes, distances = parseLabels(labels)

N = 40
# for N in range(0, len(paths)):
#     distN = distances[N]
#     labelN = labels[N]
#     print(distN)
#     print(labelN)
#     logarithmic_corrected = exposure.adjust_log(images[N], 2)
#     #fig, ax = try_all_threshold(logarithmic_corrected, figsize=(10, 8), verbose=False)
#     #plt.show()
distN = distances[N]
labelN = labels[N]
logarithmic_corrected = exposure.adjust_log(images[N], 2)

blobRadiusAlg(logarithmic_corrected, distN)

#imshow(label_im)
ski.io.show()