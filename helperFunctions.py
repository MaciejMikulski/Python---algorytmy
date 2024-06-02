import glob
import os
import re
from typing import List

import numpy as np
from skimage.io import imread, imshow
import matplotlib.pyplot as plt


def getImages(path, imType='png'):
    imPaths = glob.glob(os.path.join(path, '*.'+str(imType)))

    images = []
    for i in range(len(imPaths)):
        images.append(imread(imPaths[i]))

    imLabels = []
    for i in range(len(imPaths)):
        imLabels.append((re.findall("[0-9]-[0-9]-[0-9]", imPaths[i]))[0])

    return imLabels, np.array(images), imPaths

def parseLabels(labels):
    markerType = []
    distance = []

    for i in range(len(labels)):
        tmp = labels[i]
        markerType.append(int(tmp[0:1]))
        distance.append(float(tmp[2:3])*150.0)

    return np.array(markerType), np.array(distance)

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

def showImages(images: List[np.ndarray]) -> None:
    n: int = len(images)
    f = plt.figure()
    for i in range(n):
        # Debug, plot figure
        f.add_subplot(1, n, i + 1)
        plt.imshow(images[i])

    plt.show(block=True)