import numpy as np

def thresholdVal(image, val, datType=np.uint8):
    tmp = image >= val
    return tmp.astype(datType)

def thresholdMaxValOffset(image, offset, datType=np.uint8):
    maxVal = np.amax(image)
    tmp = image >= maxVal - offset
    return tmp.astype(datType)

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


