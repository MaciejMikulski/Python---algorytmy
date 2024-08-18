import math

from skimage.measure import label, regionprops

from helperFunctions import *
from threshold import *

class blobRadiusAlg:


    def PnPAlgorithm(self, img, distance, markerType=2):
        """
        This function performs marker detection based on positions of
        detected blobs and estimating camera orientation with the use of
        PnP method.

        Parameters
        ----------
        img : ndarray
            Gray-scale image to be processed.
        distance : float
            Approximate distance form the camera to the marker.
        markerType : int
            Describes type of marker to be detected.
                1 - marker A (Maciej's marker)
                2 - marker B (Olgierd's marker)

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

        # Number of brightest pixels in the image that shall be considered as part of the marker
        # Found in simulation on test images.
        area = 380 

        ####################################### THRESHOLDING ############################################
        binary = thresholdCumulativeHistogramArea(img, area, 0)

        ############################### CONNECTED COMPONENT LABELING ########################################
        # Label all blobs on the image ang get their parameters
        labelIm, blobNum = label(binary, background=0, connectivity=1, return_num=True)
        blobProperties = regionprops(labelIm)
        # Get area and bounding box of all the blobs
        blobArea = np.zeros((blobNum,))
        boundingBox = np.zeros((blobNum, 4))
        for i in range(blobNum):
            blobArea[i] = blobProperties[i].area
            boundingBox[i,:] = np.array(blobProperties[i].bbox)
        # If threre are less than 3 blobs left, marker crertainly not detectable, exit
        if len(blobArea) < 4:
            return x, y, rot
        
        ########################################## AREA FILTRATION #################################################
        # Remove blobs that are too small or too big
        delBlobsIm, blobArea, blobBoundBox = self.removeBlobsArea(labelIm, blobArea, boundingBox, area)
        # Save number of blobs that are present in the image 
        blobNum = len(blobArea)

        ################################### BLOB CENTERS CALCULATION ###############################
        # Find coordinates of blob centers
        blobCenters = self.getBlobCenterCoords(blobBoundBox)
        blobCenters = blobCenters.astype(int)
        # And append them to an image
        # blobCentersIm = np.zeros_like(delBlobsIm)
        # for i in range(len(blobCenters)):
        #     x = (int)(blobCenters[i, 0])
        #     y = (int)(blobCenters[i, 1])
        #     blobCentersIm[x, y] = 10 * i + 10
        # showImages([blobCentersIm], 1, 1)

        ################################### FIND MARKER BLOBS ###############################
        # Find which blobs belong to marker (if any).
        markerPoints = self.findMarkerPoints(blobCenters)
        print(markerPoints)
        #showImages([img, imageWithPoints(markerPoints, 120, 160)], 1, 2)
        # Find all non-duplicate angles between found blob centers
        # blobAngles = self.getBlobAngles(blobCenters, mode='All')

        return x, y, rot, len(blobArea)


    def removeBlobsArea(self, img, areas, bboxes, expectArea):
        """
        This method removes blobs on the image that have area smaller or bigger than specified.
        It also removes corresponding data in area an bounding box arrays.

        Parameters
        ----------
        img : ndarray
        
        areas : ndarray
        
        bboxes : ndarray
        
        expectArea : int

        Returns
        ----------
        deletedBlobsIm : ndarray
            Input image with removed blobs with areas outside of specified range.
        rmAreas : ndarray
            List of blob areas with removed elements corresponding to deleted blobs.
        rmBboxes : ndarray
            List of blob bounding boxes with removed elements corresponding to deleted blobs.
        """
        arLoBound = 8 # Value found based on simulation with test images
        arHiBound = (int)(2.0 * expectArea)

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
        centers = np.zeros((len(bboxes), 2))
        for i in range(len(bboxes)):
            minCol = bboxes[i, 0]
            minRow = bboxes[i, 1]
            maxCol = bboxes[i, 2]
            maxRow = bboxes[i, 3]
            x = (int)((minCol + maxCol) / 2)
            y = (int)((minRow + maxRow) / 2)
            centers[i, 0] = x
            centers[i, 1] = y

        return np.array(centers)

    def calculateAnglePoints(self, p1x, p1y, p2x, p2y, p3x, p3y):
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
        centersNumber = centers.shape[0]
        anglesIndexes = None

        
        if mode == 'All':
            # Get all combination of non-repeating point indexes
            anglesIndexes = []
            for i in range(centersNumber):
                for j in range(centersNumber):
                    for k in range(centersNumber):
                        if (j != i and k != i and j != k and j < k):
                        # j < k, Otherwise current point is duplicate
                            anglesIndexes.append((i, j, k))
            anglesIndexes = np.array(anglesIndexes)
                            
        elif mode == 'Closest':
            anglesIndexes = np.zeros((centersNumber, 3), dtype=int)
            # Find two closes neighbours for all points
            # Array holding distances between all pairs of points
            distances = np.zeros((centersNumber, centersNumber))
            # For every point ...
            for i in range(centersNumber):
                distancesOnePoint = np.zeros((centersNumber,)) # create array of distances to all points (incl. to itself), ...
                p1 = centers[i,:] # get current point, ...
                for j in range(centersNumber):
                    p2 = centers[j,:] # get second point ...
                    distancesOnePoint[j] = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) # and calculate distance.
                distances[i,:] = distancesOnePoint # Add them to the main array
            
            closestDist = np.copy(distances)
            closestDist.sort(axis=1) # Get distances to 2 closest neighbours by sorting the array ...
            closestDist = closestDist[:,1:3] # ... and getting 2 smallest (excluding distance to self - 0.0)

            tmpBlobPairIndexes = np.zeros((2,))
            for i in range(centersNumber):
                pairIndex = 0 # Index of the place in the pair where the blob index should be stored
                for j in range(centersNumber):
                    if distances[i, j] == closestDist[i, 0] or distances[i, j] == closestDist[i, 1]:
                        tmpBlobPairIndexes[pairIndex] = j # Save index of one of the closest blobs
                        pairIndex += 1 # Save the next index in other place in the pair
                #Save current blob index and two closest neighbours to get 3 angle vertecies
                anglesIndexes[i, 0] = i
                anglesIndexes[i, 1] = tmpBlobPairIndexes[0]
                anglesIndexes[i, 2] = tmpBlobPairIndexes[1]

        angles = np.zeros((anglesIndexes.shape[0],))
        # Calculate angles
        for i in range(anglesIndexes.shape[0]):
            p1x = centers[anglesIndexes[i, 0], 0]
            p1y = centers[anglesIndexes[i, 0], 1]
            p2x = centers[anglesIndexes[i, 1], 0]
            p2y = centers[anglesIndexes[i, 1], 1]
            p3x = centers[anglesIndexes[i, 2], 0]
            p3y = centers[anglesIndexes[i, 2], 1]
            angles[i] = self.calculateAnglePoints(p1x, p1y, p2x, p2y, p3x, p3y)

        return angles

    def findMarkerPoints(self, centers):
        """
        This method removes returns 4 points coordinates that make up marker.
        Points are always ordered: P0, P1, P2, P3.

        Parameters
        ----------
        centers: ndarray
            2D array containing coordinates of all blob centers detected in the image

        Returns
        ----------
        ndarray containing coordinates of points that make up marker in oreder: P0, P1, P2, P3.
        If no marker is detected all points have coordinates (0,0)
        """
        markerPoints = np.zeros((4,2))
        blobNum = centers.shape[0]
        tripletNum = blobNum**3 - 3*blobNum**2 + 2*blobNum # n * (n-1) * (n-2)
        pointTriplets = np.zeros((tripletNum,3))
        # Store indexes of other points to use them in checking which one may fit the vector base
        otherPoints = np.zeros((tripletNum,blobNum-3))
        cnt = 0
        possibleIndexes = np.arange(blobNum)
        for i in range(blobNum):
            for j in range(blobNum):
                for k in range(blobNum):
                    if i != j and j != k and i != k:
                        pointTriplets[cnt, 0] = i
                        pointTriplets[cnt, 1] = j
                        pointTriplets[cnt, 2] = k
                        mask = np.isin(possibleIndexes, pointTriplets[cnt,:], True, True)
                        otherPoints[cnt,:] = possibleIndexes[mask]
                        cnt += 1
        pointTriplets = pointTriplets.astype(int)
        otherPoints = otherPoints.astype(int)
        
        # Calculate predicted placement of fourth point
        expectedP3 = np.zeros((tripletNum, 2))
        distanceErr = np.zeros((tripletNum, otherPoints.shape[1]))
        crossProducts = np.zeros((tripletNum,))
        for i in range(tripletNum):
            # Get coordinates of points from triplet triplets
            p0 = centers[pointTriplets[i, 0],:]
            p1 = centers[pointTriplets[i, 1],:]
            p2 = centers[pointTriplets[i, 2],:]
            # Calculate base vectors
            v0 = p1 - p0
            v1 = p2 - p1
            expectedP3[i,:] = p0 + 0.5 * (v1 - v0)
            # Check for correct orientation of base vectors
            crossProducts[i] = np.cross(v0,v1)
            # Calculate distance of predicted points to all other (not in triplet) points
            for j in range(otherPoints.shape[1]):
                pa = expectedP3[i,:]
                pb = centers[otherPoints[i,j],:]
                distanceErr[i,j] = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)

        # TODO: add selection based on absolute value of min error and return if it is too big
        # Find the indices of all occurrences of the minimum value
        indices = np.argwhere(distanceErr == np.min(distanceErr))

        # Perform final selection of marker points
        for i in range(indices.shape[0]):
            if crossProducts[indices[i,0]] < 0.0:
                markerPoints[0,:] = centers[pointTriplets[indices[i,0], 0],:]
                markerPoints[1,:] = centers[pointTriplets[indices[i,0], 1],:]
                markerPoints[2,:] = centers[pointTriplets[indices[i,0], 2],:]
                markerPoints[3,:] = centers[otherPoints  [indices[i,0], 0],:]

        #im = np.zeros((indices.shape[0], 120, 160))
        #imList = [img]
        #for i in range(im.shape[0]):
        #    imList.append(im[i,:,:])
        #showImages(imList, 1, len(imList))

        return markerPoints.astype(int)