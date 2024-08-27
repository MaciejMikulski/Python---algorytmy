import glob
import os
import re
from typing import List

import cv2
import numpy as np
from skimage.io import imread
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

    # No subfolders, get images from the path
    if len(subdirectories) == 0:
        subdirectories = [path]

    images = []
    markerType = np.array([])
    distance = np.array([])
    id = np.array([])
    filenames = []
    paths = []
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
            _, tail = os.path.split(imPaths[i])
            if match:
                tmpMarkerType[i] = match[0][0]
                tmpDistance[i] = match[0][1]
                tmpId[i] = match[0][2]
                filenames.append(tail)
            else:
                raise Exception("Invalid image label: " + str(match))   
        # Append labels found in current folder to list of all labels
        markerType = np.append(markerType, tmpMarkerType)
        distance = np.append(distance, tmpDistance)
        id = np.append(id, tmpId)

    print("")
    return np.array(images), markerType, distance, id, filenames

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

def presentImages(images, rows, cols):
    imagesNum = images.shape[0]
    for i in range(0, len(images), 25):
        if i + 25 < imagesNum:
            showImages(images[i:i+25,:,:], rows, cols, str(i) + ' - ' + str(i+25))
        else:
            showImages(images[i:imagesNum,:,:], rows, cols, str(i) + ' - ' + str(imagesNum))

def showImages(images: List[np.ndarray], rows, cols, title='', subtitles=None) -> None:
    n: int = len(images)    
    f = plt.figure(figsize=(10,10))
    f.suptitle(title)

    for i in range(n):
        # Debug, plot figure
        ax = f.add_subplot(rows, cols, i + 1)
        if subtitles != None:
            ax.set_title(subtitles[i])
        plt.imshow(images[i])

    plt.show(block=True)

def imageWithPoints(points, imHeight, imWidth, backgroundIm=None):
    """
    This method creates image with given points or appends points into given image.
    """
    pointNum = points.shape[0]
    tmpPoints = points.astype(int)
    if backgroundIm == None:
        im = np.zeros((imHeight, imWidth))
    else:
        im = np.copy(backgroundIm)
    pointValues = np.linspace(0, 255, pointNum+1)

    for i in range(pointNum):
        im[tmpPoints[i,0], tmpPoints[i,1]] = pointValues[i+1]
    return im

def imagePnPoverlay(img, marker2Dpoints, rotVect, transVect, cameraMatrix):
    """
    This method append marker points onto image and draws a vector normal to the marker surface.
    """
    imagePnP = np.copy(img)
    (lineEndPoint, _) = cv2.projectPoints(np.array([(0.0, 0.0, 1.0)]), rotVect, transVect, cameraMatrix, None)

    for p in marker2Dpoints:
        cv2.circle(imagePnP, (int(p[1]), int(p[0])), 2, (0,0,255), -1)
    
    p1 = ( int(marker2Dpoints[0][1]), int(marker2Dpoints[0][0]))
    p2 = ( int(lineEndPoint[0][0][1]), int(lineEndPoint[0][0][0]))
    
    cv2.line(imagePnP, p1, p2, (255,0,0), 1)
    return imagePnP

def unevenVectorsToArray(v):
    """
    This method vreates an nunmpy array form a list of vectors with uneven lenghts.
    Elements not present in shorter vectors are filled with 0.
    """
    lens = np.array([len(item) for item in v])
    mask = lens[:,None] > np.arange(lens.max())
    out = np.zeros(mask.shape,dtype=int)
    out[mask] = np.concatenate(v)
    return out

