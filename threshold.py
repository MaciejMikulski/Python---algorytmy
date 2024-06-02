import numpy as np

def thresholdVal(image, val, datType=np.uint8):
    tmp = image >= val
    return tmp.astype(datType)

def thresholdMaxValOffset(image, offset, datType=np.uint8):
    maxVal = np.amax(image)
    tmp = image >= maxVal - offset
    return tmp.astype(datType)

