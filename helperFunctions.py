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
    markerType = np.array([])
    distance = np.array([])
    id = np.array([])
    for j in range(len(subdirectories)):
        print('.', end="")
        # Get paths of all images in current subdirectory
        imPaths = glob.glob(os.path.join(subdirectories[j], '*.'+str(imType)))
        # Read all images
        for i in range(len(imPaths)):
            images.append(imread(imPaths[i]))

        # Parse all labels
        tmpMarkerType = np.zeros((len(imPaths),))
        tmpDistance = np.zeros((len(imPaths),))
        tmpId = np.zeros((len(imPaths),))
        for i in range(len(imPaths)):
            match = re.findall(r"(\d+)-(\d+)-(\d+)", imPaths[i])
            if match:
                tmpMarkerType[i] = match[0][0]
                tmpDistance[i] = match[0][1]
                tmpId[i] = match[0][2]
            else:
                raise Exception("Invalid image label: " + str(match))   
        # Append labels found in current folder to list of all labels
        markerType = np.append(markerType, tmpMarkerType)
        distance = np.append(distance, tmpDistance)
        id = np.append(id, tmpId)

    return np.array(images), markerType, distance, id, imPaths

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

def showImages(images: List[np.ndarray], rows, cols, title='') -> None:
    n: int = len(images)
    f = plt.figure()
    f.suptitle(title)
    for i in range(n):
        # Debug, plot figure
        f.add_subplot(rows, cols, i + 1)
        plt.imshow(images[i])

    plt.show(block=True)