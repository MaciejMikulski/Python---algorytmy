import numpy as np
import queue

def hardwareCCL(img, dispImg=False):
    """
    This is a software prototype of one-pass CCL function taken from arcicle.
    It takes binary image and fings blobs and their bounding boxes. 

    Parameters:
    -----------
    img: ndarray
        Array containing thresholded binary image.
    
    Returns:
    --------
    blobNum: int
        Number of detected blobs.
    blobArea: ndarray
        Vector containing areas of detected blobs.
    boundingBoxes: ndarray
        4xblobNum array containing xmin, xmax, ymin and ymax vales of bBox.
    labelIm: ndarray
        Image with each blob having its own color.
    """
    blobNum = 0
    blobArea = []
    boundingBoxes = []
    labelIm = np.zeros_like(img) 

    imgSizeY = img.shape[0]
    imgSizeX = img.shape[1]
    # CCL variables: registers, FIFO, data structures etc.
    # Data comes in like that: img -> X -> D -> lineBuf -> C -> B -> A
    lineBuf = queue.Queue() # Buffer for 1 line of image. Keep empty, during first row it will be filled.
    tmpBufRead = 0 # Variable used for storing and compasisons of labels extracted from lineBuffer
    for _ in range(0, imgSizeX+1): lineBuf.put(0) # Initialise buffer with 0
    mergeStack = queue.LifoQueue()
    mergeFlag = False

    Areg = 0   # Registers making up the window
    Breg = 0
    Creg = 0
    Dreg = 0
    Awin = 0   # Window elements - either their register value or 0
    Bwin = 0
    Cwin = 0
    Dwin = 0
    X = 0 # Currently evaluated pixel
    AD = 0
    minLabel = 1
    mergerTable = np.zeros((128,)).astype(int) # Merger table fot N different labels

    for y in range(0, imgSizeY):
        # On the beginning of each line preload B and C registers from line buffer        
        Breg = mergerTable[lineBuf.get()]
        Creg = mergerTable[lineBuf.get()]
        for x in range(0, imgSizeX):
            # Window creation
            Awin = 0 if (x == 0 or y == 0)          else Areg
            Bwin = 0 if (y == 0)                    else Breg
            Cwin = 0 if (x == imgSizeX-1 or y == 0) else Creg
            Dwin = 0 if (x == 0)                    else Dreg
            # Label selection
            AD = Awin | Dwin # AD is A or D label (when they are both non 0 they MUST have the same value)
            if (img[y, x] == 1): # Foreground pixel - give it label
                if (AD == 0 and Bwin == 0 and Cwin == 0): # New label operation
                    X = minLabel # Assign new label to current pixel
                    minLabel += 1 # Increment new label ID
                    mergerTable[X] = X # Init merger table to point to itself
                elif(AD != 0 and Cwin != 0 and Bwin == 0 and AD != Cwin): # Merge operation
                    mergeFlag = True
                    Lmin = min(AD, Cwin)
                    Lmax = max(AD, Cwin)
                    X = Lmin # Assign X to min of two encountered labels
                    mergerTable[Lmax] = Lmin # Update merger table
                    mergeStack.put((Lmin, Lmax)) # Push Lmin, Lmax pair to stack for path compression
                    if(dispImg):
                        if(Awin != 0 and x != 0 and y != 0): labelIm[y-1, x-1] = Lmin
                        if(Dwin != 0 and x != 0): labelIm[y, x-1] = Lmin
                        if(x != imgSizeX-1 and y != 0): labelIm[y-1, x+1] = Lmin
                else: # Copy operation - one or more regs contain label L
                    X = AD | Bwin | Cwin # ORing simply extracts L value from regs, no matter in which one it is
            else: # Background pixel - give it label 0
                X = 0
            # Clock-cycle data assignment
            lineBuf.put(Dreg)
            Dreg = X
            Areg = Breg
            tmpBufRead = mergerTable[lineBuf.get()]
            if(mergeFlag): 
                mergeFlag = 0
                Breg = X
                Creg = tmpBufRead if(tmpBufRead == 0) else X
            else:
                Breg = Creg
                Creg = tmpBufRead
            if(dispImg): 
                labelIm[y,x] = X # Add current pixel to labeled image
                if (x < imgSizeX-1 and y != 0): # Account for mergers in output image
                    if(Breg != labelIm[y-1, x+1]): labelIm[y-1, x+1] = Breg
                    if(Areg != labelIm[y-1, x]):   labelIm[y-1, x] = Areg
        # End of Line path compression
        lineBuf.put(Dreg)
        lineBuf.put(0)
        Dreg = 0
        while(not mergeStack.empty()):
            (Lmin, Lmax) = mergeStack.get() # Pop off label pairs from stack
            mergerTable[Lmax] = mergerTable[Lmin] # And update merger table to compress paths

    return blobNum, blobArea, boundingBoxes, labelIm


image = np.random.randint(low=0, high=2, size=(5,5))
#image = np.array([[1, 1, 0, 1, 1], [0, 0, 0, 1, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [1, 1, 1, 1, 0]])
#image = np.array([[1, 0, 0, 0, 1], [0, 1, 1, 1, 0], [1, 0, 1, 1, 1], [0, 0, 0, 0, 0], [1, 1, 1, 1, 0]])
#image = np.array([[1, 0, 1, 1, 0], [1, 1, 0, 0, 0], [1, 0, 0, 1, 1], [1, 0, 1, 0, 1], [0, 0, 0, 1, 0]])

a, b, c, labelImg = hardwareCCL(image, True)
print(image)
print(" ")
print(labelImg)