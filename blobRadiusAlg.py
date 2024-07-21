import math

from skimage.filters import threshold_minimum, threshold_mean
from skimage.measure import label, regionprops

from helperFunctions import *
from threshold import *

class blobRadiusAlg:


    def blobAlgorithm(self, img, distance, offset, markerType=1):
        """
        This function performs marker detection algorithm based on
        blob detection and search of other squares in a radius around
        another.

        Parameters
        ----------
        img : ndarray
            Gray-scale image to be processed.
        distance : float
            Approximate distance form the camera to the marker.
        markerType : int
            Describes type of marker to be detected.
                1 - marker A (Olgierd's marker)
                2 - marker B (Maciej's marker)

        Returns
        ----------
        x : int
            Position of the marker in x axis. Set to 255 if no marker 
            is detected.
        y : int
            Posiion of the market in y axis.
        rot : float
            Rotation of the marker.
        """
        x: int = 255
        y: int = 0
        rot = 0.0

        ####################################### THRESHOLDING ############################################
        expectedBlobArea = getSizeInPixels(1.0, distance) ** 2

        binary = thresholdCumulativeHistogramArea(img, expectedBlobArea * 2, offset)

        ############################### CONNECTED COMPONENT LABELING ########################################
        # Label all blobs on the image ang get their parameters
        labelIm, blobNum = label(binary, background=0, connectivity=1, return_num=True)
        blobProperties = regionprops(labelIm)
        # Get area and bounding box of all the blobs
        area = []
        boundingBox = []
        for i in range(blobNum):
            area.append(blobProperties[i].area)
            boundingBox.append(blobProperties[i].bbox)
        blobArea = np.array(area)
        blobBoundBox = np.array(boundingBox)



        # If threre are less than 3 blobs left, marker crertainly not detectable, exit
        #if len(blobArea) < 4:
        #    return x, y, rot
        
        ########################################## AREA FILTRATION #################################################
        # Expected area in pixels of one square of the marker (blob)
        expectedBlobArea = getSizeInPixels(1.0, distance) ** 2

        # Remove blobs that are too small or too big
        delBlobsIm, blobArea, blobBoundBox = self.removeBlobsArea(labelIm, blobArea, blobBoundBox, expectedBlobArea, 0.3, 1.7)

        return len(blobArea)

        ################################### ANGLE CALCULATION ###############################
        blobAngles = []
        # Find coordinates of blob centers
        blobCenters = self.getBlobCenterCoords(blobBoundBox)
        # And append them to an image
        # blobCentersIm = np.copy(delBlobsIm)
        # for i in range(len(blobCenters)):
        #     x = (int)(blobCenters[i, 0])
        #     y = (int)(blobCenters[i, 1])
        #     blobCentersIm[x, y] = 100.0
        # Find all non-duplicate angles between found blob centers
        blobAngles = self.getBlobAngles(blobCenters, mode='Closest')
        #showImages([img, labelIm, delBlobsIm, blobCentersIm], str(len(blobArea)))
        #else:
        #showImages([img, labelIm, delBlobsIm], str(len(blobArea)))
        
        return x, y, rot, len(blobArea), blobAngles


    def removeBlobsArea(self, img, areas, bboxes, expectArea, areaLowBound, areaHighBound):
        """
        This method removes blobs on the image that have area smaller or bigger than specified.
        It also removes corresponding data in area an bounding box arrays.

        Parameters
        ----------
        img : ndarray
        
        areas : ndarray
        
        bboxes : ndarray
        
        expectArea : int
        
        areaLowBound : float
        
        areaHighBound : float


        Returns
        ----------
        deletedBlobsIm : ndarray
            Input image with removed blobs with areas outside of specified range.
        rmAreas : ndarray
            List of blob areas with removed elements corresponding to deleted blobs.
        rmBboxes : ndarray
            List of blob bounding boxes with removed elements corresponding to deleted blobs.
        """
        arLoBound = (int)(areaLowBound * expectArea)
        arHiBound = (int)(areaHighBound * expectArea)

        removeIndexes = []
        for i in range(len(areas)):
            if areas[i] < arLoBound or areas[i] > arHiBound:
                removeIndexes.append(i)
        rmAreas = np.delete(areas, removeIndexes)
        rmBboxes = np.delete(bboxes, removeIndexes, axis=0)

        # Set removed blobs to 0 - background color
        deletedBlobsIm = np.copy(img)
        removeIndexes = np.array(removeIndexes) + 1
        for x in range(deletedBlobsIm.shape[0]):
            for y in range(deletedBlobsIm.shape[1]):
                # Indexes start from 0, but blob labels start from 1, add 1 to index
                if (deletedBlobsIm[x][y]) in removeIndexes:
                    deletedBlobsIm[x][y] = 0
        return deletedBlobsIm, rmAreas, rmBboxes

    def getBlobCenterCoords(self, bboxes):
        """
        Returns coordinates of blobs with given bounding boxes.

        Parameters
        ----------
        bboxes : ndarray
        Array of bounding boxes form scikit regionprops.

        Returns
        ----------
        centers : ndarray
        Coordinates of blob centers. [][0] is x and [][1] is y coordinate.
        """
        centers = []
        for i in range(len(bboxes)):
            minCol = bboxes[i, 0]
            minRow = bboxes[i, 1]
            maxCol = bboxes[i, 2]
            maxRow = bboxes[i, 3]
            x = (int)((minCol + maxCol) / 2)
            y = (int)((minRow + maxRow) / 2)
            centers.append((x, y))

        return np.array(centers)

    def calculateAnglePoints(p1x, p1y, p2x, p2y, p3x, p3y):
        numerator = p2y*(p1x-p3x) + p1y*(p3x-p2x) + p3y*(p2x-p1x)
        denominator = (p2x-p1x)*(p1x-p3x) + (p2y-p1y)*(p1y-p3y)
        eps = 0.001
        if -eps < denominator < eps: denominator = 0.001
        ratio = numerator / denominator

        angleRad = math.atan(ratio)
        angleDeg = (angleRad*180)/math.pi;

        if angleDeg < 0.0 :
            angleDeg = 180.0 + angleDeg

        return angleDeg

    def getBlobAngles(self, centers, mode='All'):
        """
        This function calculates all angles between combinations of 3 center points.

        Parameters:
        -----------
        centers : ndarray
        XY coordinates of blobs detested in the image.

        mode : string
            'All' - get angles between all 3-point sets
            'Closest' - get angles for all points and their two closest neighbours

        Returns:
        -----------
        angles : ndarray
        Angles in degrees of all combinations of center points, without duplications.
        With mode 'All" they are orederd by vertecies indexes: 012, 013, ... 023, 102 ect.
        With mode 'Closest' for one center point there is one angle. Angles are orederd by 
        center vertex index.
        """
        anglesIndexes = []
        angles = []
        if mode == 'All':
            # Get all combination of non-repeating point indexes
            for i in range(centers.shape[0]):
                for j in range(centers.shape[0]):
                    for k in range(centers.shape[0]):
                        if (j != i and k != i and j != k and j < k):
                        # j < k, Otherwise current point is duplicate
                            anglesIndexes.append((i, j, k))
        elif mode == 'Closest':
            # Find two closes neighbours for all points
            # List of tuples. Each tuple holds distances from all other points
            distances = []
            for i in range(centers.shape[0]):
                tmpDist = [] # Tuple containing distances to all points
                p1 = centers[i,:] # Get current point
                for j in range(centers.shape[0]):
                    p2 = centers[j,:] # Get second point
                    tmpDist.append(math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2))
                distances.append(tmpDist)
            distances = np.array(distances)
            closestDist = np.copy(distances)
            closestDist.sort(axis=1)
            closestDist = closestDist[:,1:3] # Get distances to 2 closest neighbours

            for i in range(distances.shape[0]):
                tmpIndexPair = []
                for j in range(distances.shape[1]):
                    if distances[i, j] == closestDist[i, 0] or distances[i, j] == closestDist[i, 1]:
                        tmpIndexPair.append(j) # Save index of one of the closest blobs
                #Save current blob index and two closest neighbours to get 3 angle vertecies
                anglesIndexes.append([i, tmpIndexPair[0], tmpIndexPair[1]])
            anglesIndexes = np.array(anglesIndexes)

        # Calculate angles
        for i in range(len(anglesIndexes)):
            p1x = centers[anglesIndexes[i][0], 0]
            p1y = centers[anglesIndexes[i][0], 1]
            p2x = centers[anglesIndexes[i][1], 0]
            p2y = centers[anglesIndexes[i][1], 1]
            p3x = centers[anglesIndexes[i][2], 0]
            p3y = centers[anglesIndexes[i][2], 1]
            angles.append(self.calculateAnglePoints(p1x, p1y, p2x, p2y, p3x, p3y))

        return angles
