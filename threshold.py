import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from helperFunctions import *

def thresholdVal(image, val, datType=np.uint8):
    thresholdedImage = image >= val
    return thresholdedImage.astype(datType)

def thresholdMaxValOffset(image, offset, datType=np.uint8):
    maxVal = np.amax(image)
    thresholdedImage = image >= maxVal - offset
    return thresholdedImage.astype(datType)

def thresholdHistogramMaxOffset(image, offset, datType=np.uint8):
        """
        Calculates histogram of the image and calculates threshold
        as the max of the histogram with added offset (negative or positive).
        If the offset is too big, the threshold values are claped.

        Parameters
        ----------
        imgage : ndarray
            Gray-scale image to be processed.
        offset : int
            Offset added to the found histogram peak. May be negative or positive.
        dataType
            Type of image data to be returned.

        Returns
        ----------
        Image thresholded with the use of calculated threshold value.
        """
        # Calculate histogram with 256 bins corresponding to all possible pixel values
        hist, _ = np.histogram(image, bins=255, range=(0.0, 0.0))
        thresholdedImage = image >= np.clip(np.max(hist) + offset, 0, 255)
        return thresholdedImage.astype(datType)

def thresholdCumulativeHistogramArea(image, markerArea, offset=0, datType=np.uint8):
        """
        Calculates cumulative histogram of the image and calculates threshold
        based on the predicted area of the marker. N brightest pixels which would 
        create marker are set to foreground, the rest is set to background.

        Parameters
        ----------
        imgage : ndarray
            Gray-scale image to be processed.
        markerArea : int
            Predicted area of the marer on the image.
        dataType
            Type of image data to be returned.

        Returns
        ----------
        Image thresholded with the use of calculated threshold value.
        """
        # Calculate histogram with 256 bins corresponding to all possible pixel values
        histogram, _ = np.histogram(image, bins=255, range=(0.0, 255.0))
        # Calculate predicted number of background pixels
        backgroundArea = image.shape[0] * image.shape[1] - markerArea
        cumulativeHistogram = 0
        thresholdValue = 0
        # Calculate threshold - number of bin in which cumulative histogram surpasses the predicted
        # number of background pixels background 
        for i in range(len(histogram)):
            cumulativeHistogram += histogram[i]
            if cumulativeHistogram > backgroundArea:
                  thresholdValue = i
                  break
        thresholdedImage = image >= np.clip(thresholdValue + offset, 0, 255)
        return thresholdedImage.astype(datType)
