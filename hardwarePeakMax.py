import numpy as np
from helperFunctions import *
import math

def hardwarePeakMax(img, thres, minDist):
    kernelSize: int = 13
    kernelPadding = kernelSize//2

    sizeY = img.shape[0]
    sizeX = img.shape[1]
    maxFilterOut = np.copy(img)
    # Max filter
    for y in range(sizeY):
        for x in range(sizeX):
            # Generate kernel - current pixel neighborhood
            kernel = np.zeros((kernelSize, kernelSize))
            for ky in range(-kernelSize//2+1, kernelSize//2+1, 1):
                for kx in range(-kernelSize//2+1, kernelSize//2+1, 1):
                    if y+ky < 0 or y+ky >= sizeY or x+kx < 0 or x+kx >= sizeX:
                        kernel[ky+kernelPadding, kx+kernelPadding] = 0
                    else:
                        kernel[ky+kernelPadding, kx+kernelPadding] = img[y+ky, x+kx]
            # Find max pixel in the kernel
            maxKernelPix = 0
            for ky in range(kernelSize):
                for kx in range(kernelSize):
                    if kernel[ky, kx] > maxKernelPix: 
                        maxKernelPix = kernel[ky, kx]
            # and assign it to current pixel
            maxFilterOut[y, x] = maxKernelPix
    
    peakMax = (img == maxFilterOut)
    peakMax &= img > thres
    coords = np.transpose(np.nonzero(peakMax))
    print(coords)
    numCoords = coords.shape[0]
    removedCoords = []
    # Remove all points that are too clode to each other
    for i in range(numCoords):
        for j in range(i, numCoords, 1):
            if i == j: continue
            dist = math.sqrt((coords[i,0]-coords[j,0])**2+(coords[i,1]-coords[j,1])**2)
            if dist < minDist:
                removedCoords.append(coords[i])
                break
    removedCoords = np.array(removedCoords)
    coordsFiltered = setdiff_nd(coords, removedCoords)
    print(coordsFiltered)
    showImages([img, peakMax, imageWithPoints(coordsFiltered,img.shape[0], img.shape[1])], 1, 3)


def view1D(a, b): # a, b are arrays
    a = np.ascontiguousarray(a)
    b = np.ascontiguousarray(b)
    void_dt = np.dtype((np.void, a.dtype.itemsize * a.shape[1]))
    return a.view(void_dt).ravel(),  b.view(void_dt).ravel()

def setdiff_nd(a,b):
    # a,b are the nD input arrays
    A,B = view1D(a,b)    
    return a[~np.isin(A,B)]
#hardwarePeakMax()