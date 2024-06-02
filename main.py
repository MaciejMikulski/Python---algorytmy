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

maciekMarkerLabels = []
olgierdMarkerLabels = []
noMarkerLabels = []
maciekMarkerAngles = []
olgierdMarkerAngles = []
for N in range(0, len(paths)):
    distN = distances[N]
    labelN = labels[N]
    markerTypeN = markerTypes[N]
    x, y, rot, blobNum, angles = blobRadiusAlg(images[N], distN)

    if blobNum >= 4:
        if markerTypeN == 1:
            maciekMarkerLabels.append(labelN)
            maciekMarkerAngles.append(angles)
        elif markerTypeN == 2:
            olgierdMarkerLabels.append(labelN)
            olgierdMarkerAngles.append(angles)
    else:
        noMarkerLabels.append(labelN)

    # while True:
    #     resp = str(input())
    #     print('Resp: ', resp)
    #     if resp == 'y':
    #         if markerTypeN == 1:
    #             maciekMarkerLabels.append(labelN)
    #         elif markerTypeN == 2:
    #             olgierdMarkerLabels.append(labelN)
    #         break
    #     elif resp == 'n':
    #         noMarkerLabels.append(labelN)
    #         break
    #     else:
    #         print('Invalid response')

maciekMarkerAngles = np.around(np.array(maciekMarkerAngles)/5, decimals=0)*5
olgierdMarkerAngles = np.around(np.array(olgierdMarkerAngles)/5, decimals=0)*5

maciekMarkerAngles.sort(axis=1)
olgierdMarkerAngles.sort(axis=1)
print(maciekMarkerAngles)
print(olgierdMarkerAngles)

#print(maciekMarkerLabels)
#print(olgierdMarkerLabels)
#print(noMarkerLabels)
    #fig, ax = try_all_threshold(logarithmic_corrected, figsize=(10, 8), verbose=False)
    #plt.show()

#N = 40
#distN = distances[N]
#labelN = labels[N]
#logarithmic_corrected = exposure.adjust_log(images[N], 2)

#blobRadiusAlg(logarithmic_corrected, distN)
#binary = thresholdMaxValOffset(images[N], 80)
#showImages([images[N], binary])
