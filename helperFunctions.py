import glob
import os
import re
from typing import List

import numpy as np
from skimage.io import imread, imshow
import matplotlib.pyplot as plt


def listSubdirectoriesRecursively(base_path):
    subdirectories = []
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            subdirectories.append(os.path.join(root, dir_name))
    return subdirectories

def getImages(path, imType='png'):
    # Get all subdirectories which contain images
    subdirectories = listSubdirectoriesRecursively(path)

    images = []
    imLabels = []
    for j in range(len(subdirectories)):
        print('.', end="")
        # Get paths of all images in current subdirectory
        imPaths = glob.glob(os.path.join(subdirectories[j], '*.'+str(imType)))
        # Read all images
        for i in range(len(imPaths)):
            images.append(imread(imPaths[i]))

        # Parse all labels
        for i in range(len(imPaths)):
            findsShort = re.findall("[0-9]-[0-9]-[0-9]", imPaths[i])
            findsLong = re.findall("[0-9]-[0-9][0-9]-[0-9]", imPaths[i])
            if len(findsShort) == 0:
                imLabels.append(findsLong[0])
            else:
                imLabels.append(findsShort[0])

    return imLabels, np.array(images), imPaths

def parseLabels(labels):
    markerType = []
    distance = []
    id = []
    for i in range(len(labels)):
        tmp = labels[i]
        markerType.append(int(tmp[0:1]))
        if len(tmp) == 5:
            distance.append(float(tmp[2:3])*150.0)
            id.append(int(tmp[4:5]))
        elif len(tmp) == 6:
            distance.append(float(tmp[2:4])*15.0)
            id.append(int(tmp[5:6]))
        else:
            pass    

    return np.array(markerType), np.array(distance), np.array(id)

def getSizeInPixels(realLifeSize, distance):
    """
    This function calculates approximate pixel length of a feature with given
    real life size, as seen from a given distance. Coefficients of the linear
    equation were found by analysing captured images of scaled marker.

    Parameters
    ----------
    realLifeSize : float
        Size of the feature in real life in meters.
    distance : float
        Distance from the camera to the feature in meters.

    Returns
    ----------
    Feature size in pixels.
    """
    a = -0.02667
    b = 34
    return int(np.rint((a * distance + b) * realLifeSize))

def showImages(images: List[np.ndarray], title='') -> None:
    n: int = len(images)
    f = plt.figure()
    f.suptitle(title)
    for i in range(n):
        # Debug, plot figure
        f.add_subplot(1, n, i + 1)
        plt.imshow(images[i])

    plt.show(block=True)