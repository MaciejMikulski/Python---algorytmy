from enum import Enum
import math
import numpy as np

from skimage.feature import peak_local_max
from skimage.measure import label, regionprops
import cv2

from helperFunctions import *
from threshold import *

class AlgorithmType(Enum):
    ALGORITHM_BLOB = 1
    ALGORITHM_PEAK = 2
    ALGORITHM_NEURAL = 3

class visualAlgorithm:

    def __init__(self, algType: AlgorithmType):
        self._algorithmType = algType

    def execute(self, img, markerType=2, dispImg=False):
        marker2DPoints = []
        algSuccess = False
        algImages = []

        if self._algorithmType == AlgorithmType.ALGORITHM_BLOB:
            marker2DPoints, firstStageSuccess, algImages = self._blobAlgorithm(img=img, displayImage=dispImg, markerType=markerType)
        elif self._algorithmType == AlgorithmType.ALGORITHM_PEAK:
            marker2DPoints, firstStageSuccess, algImages = self._peakAlgorithm(img=img, displayImage=dispImg, markerType=markerType)
        elif self._algorithmType == AlgorithmType.ALGORITHM_NEURAL:
            pass
        
        if not firstStageSuccess:
            return rotationVector, translationVector, algSuccess
        
        ################################### PERSPECTIVE-N-POINT ###############################
        f = 0.05 / 12e-6 # Convert focal length to pixel uints
        cameraMatrix = np.array(([f, 0, 0], [0, f, 0], [0, 0, 1]), dtype=np.float32)
        marker3Dpoints = np.array(([2, 0, 0], [0, -2, 0], [-2, 0, 0], [2, 2, 0]), dtype=np.float32)
        (success, rotationVectorPnP, translationVector) = cv2.solvePnP(marker3Dpoints, marker2DPoints.astype(np.float32), cameraMatrix, None)
        if not success:
            return rotationVector, translationVector, algSuccess

        rotationVector = self._rotationVectRodriguesToEuler(rotationVectorPnP) # Calculate Euler angles from Rodrigues angles 
        algSuccess = True
        
        if dispImg:
            PnPIm = imagePnPoverlay(img, marker2DPoints, rotationVectorPnP, translationVector, cameraMatrix)
            algImages.insert(0, img)
            algImages.append(PnPIm)
            self._displayAlgorithmStages(algImages)            

        return rotationVector, translationVector, algSuccess

    ################################# ALGORITHMS #################################
    def _blobAlgorithm(self, img, displayImage=False, markerType=2):
        """
        This function performs marker detection based on positions of
        detected blobs.

        Parameters
        ----------
        img : ndarray
            Gray-scale image to be processed.
        displayImage : bool
            If true, images with all stages of algorithm are displayed at the end.
        markerType : int
            Describes type of marker to be detected.
                1 - marker A (Maciej's marker)
                2 - marker B (Olgierd's marker)

        Returns
        ----------
        rotationVector: ndarray
            3x1 vector containing rotation values: psi, theta and fi respectively.
        translatioVector: ndarray
            3x1 vector containing translation values in meters.
        algSuccess: bool
            True if algorith sucessfully detected a marker.
        """
        algSuccess: bool = False
        dispImages = []
        # Number of brightest pixels in the image that shall be considered as part of the marker
        # Found in simulation on test images.
        area = 380 

        ####################################### THRESHOLDING ############################################
        binaryIm = thresholdCumulativeHistogramArea(img, area, 0)
        if displayImage: dispImages.append(binaryIm)
        ############################### CONNECTED COMPONENT LABELING ########################################
        blobNum, blobArea, boundingBox, labelIm = self._detectBlobs(binaryIm) # Label all blobs on the image ang get their 
        if displayImage: dispImages.append(labelIm)
        if blobNum < 4:
            return (marker2Dpoints, algSuccess, dispImages)
        ########################################## AREA FILTRATION #################################################
        blobArea, blobBoundBox, delBlobsIm = self._removeBlobsArea(labelIm, blobArea, boundingBox, area, displayImage) # Remove blobs that are too small or too big
        if displayImage: dispImages.append(delBlobsIm)
        ################################### BLOB CENTERS CALCULATION ###############################
        blobCenters = self._getBlobCenterCoords(blobBoundBox) # Find coordinates of blob centers
        if displayImage: dispImages.append(imageWithPoints(blobCenters, 120, 160)) # And append them to an image
        
        ################################### FIND MARKER BLOBS ###############################
        marker2Dpoints, noisePointsIm, markerFindSuccess = self._findMarkerPoints(blobCenters) # Find which blobs belong to marker (if any).
        if markerFindSuccess: algSuccess = True
        else: return marker2Dpoints, algSuccess, dispImages
        
        if displayImage: dispImages.append(noisePointsIm)
        return marker2Dpoints, algSuccess, dispImages
        
    def _peakAlgorithm(self, img, displayImage=False, markerTYpe=2):
        """
        This function performs marker detection based on positions of
        peaks of input image brightness.

        Parameters
        ----------
        img : ndarray
            Gray-scale image to be processed.
        displayImage : bool
            If true, images with all stages of algorithm are displayed at the end.
        markerType : int
            Describes type of marker to be detected.
                1 - marker A (Maciej's marker)
                2 - marker B (Olgierd's marker)

        Returns
        ----------
        marker2DPoints: ndarray
            4x2 array ontaining (x,y) coordinates of marker segments.
        algSuccess: bool
            True if algorith sucessfully detected a marker.
        dispImages: List
            List of images generated on different stages of the algorithm.
        """
        marker2Dpoints = np.zeros((4,2))
        algSuccess: bool = False
        dispImages = []
        # Minimum distance between peaks in input image brightness. Peaks closer than this value will not be detected.
        peakMinDistance = 10

        peakCoordinates = peak_local_max(img, min_distance=peakMinDistance)
        if displayImage: dispImages.append(imageWithPoints(peakCoordinates, 120, 160))
        if peakCoordinates.shape[0] < 4:
            return (marker2Dpoints, algSuccess, dispImages)

        ################################### FIND MARKER BLOBS ###############################
        marker2Dpoints, noisePointsIm, markerFindSuccess = self._findMarkerPoints(blobCenters) # Find which blobs belong to marker (if any).
        if markerFindSuccess: algSuccess = True
        else: return marker2Dpoints, algSuccess, dispImages

        if displayImage: dispImages.append(noisePointsIm)
        return marker2Dpoints, algSuccess, dispImages

    ################################# CCL HELPER FUNCTIONS #################################
    def _detectBlobs(self, img):
        labelIm, blobNum = label(img, background=0, connectivity=1, return_num=True)
        blobProperties = regionprops(labelIm)
        # Get area and bounding box of all the blobs
        blobArea = np.zeros((blobNum,))
        boundingBox = np.zeros((blobNum, 4))
        for i in range(blobNum):
            blobArea[i] = blobProperties[i].area
            boundingBox[i,:] = np.array(blobProperties[i].bbox)
        return blobNum, blobArea, boundingBox, labelIm

    def _removeBlobsArea(self, img, areas, bboxes, expectArea, dispIm=False):
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
        if dispIm:
            deletedBlobsIm = np.copy(img)
            removeIndexes = np.array(removeIndexes) + 1
            for x in range(deletedBlobsIm.shape[0]):
                for y in range(deletedBlobsIm.shape[1]):
                    # Indexes start from 0, but blob labels start from 1, add 1 to index
                    if (deletedBlobsIm[x][y]) in removeIndexes:
                        deletedBlobsIm[x][y] = 0
            return rmAreas, rmBboxes, deletedBlobsIm
        else: return rmAreas, rmBboxes

    def _getBlobCenterCoords(self, bboxes):
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

        return np.array(centers).astype(int)

    ################################# PnP HELPER FUNCTIONS #################################
    def _findMarkerPoints(self, centers, addRandPoints=False, randPointNum=0):
        """
        This method removes returns 4 points coordinates that make up marker.
        Points are always ordered: P0, P1, P2, P3.

        Parameters
        ----------
        centers: ndarray
            2D array containing coordinates of all blob centers detected in the image

        Returns
        ----------
        ndarray containing coordinates of points that make up marker in order: P0, P1, P2, P3.
        If no marker is detected all points have coordinates (0,0).

        ndarray containing image with selected points.

        bool indicating if the algorithm was successful. 
        """
        fourthBlobMaxDistanceError = 5.0
        markerPoints = np.zeros((4,2))
        success = False
        if addRandPoints:
            tmpCenters = self._addRandomPoints(centers, randPointNum)
        else:
            tmpCenters = centers
        im = imageWithPoints(tmpCenters, 120, 160)
        blobNum = tmpCenters.shape[0]
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
            p0 = tmpCenters[pointTriplets[i, 0],:]
            p1 = tmpCenters[pointTriplets[i, 1],:]
            p2 = tmpCenters[pointTriplets[i, 2],:]
            # Calculate base vectors
            v0 = p1 - p0
            v1 = p2 - p1
            expectedP3[i,:] = p0 + 0.5 * (v1 - v0)
            # Check for correct orientation of base vectors
            crossProducts[i] = np.cross(v0,v1)
            # Calculate distance of predicted points to all other (not in triplet) points
            for j in range(otherPoints.shape[1]):
                pa = expectedP3[i,:]
                pb = tmpCenters[otherPoints[i,j],:]
                distanceErr[i,j] = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)

        # TODO: add selection based on absolute value of min error and return if it is too big
        # Find the indices of all occurrences of the minimum value
        if np.min(distanceErr) < fourthBlobMaxDistanceError:
            indices = np.argwhere(distanceErr == np.min(distanceErr))
            success = True
        else:
            return markerPoints.astype(int), im, success

        # Perform final selection of marker points
        for i in range(indices.shape[0]):
            if crossProducts[indices[i,0]] < 0.0: # Discad mirror view of the marker
                markerPoints[0,:] = tmpCenters[pointTriplets[indices[i,0], 0],:]
                markerPoints[1,:] = tmpCenters[pointTriplets[indices[i,0], 1],:]
                markerPoints[2,:] = tmpCenters[pointTriplets[indices[i,0], 2],:]
                markerPoints[3,:] = tmpCenters[otherPoints  [indices[i,0], 0],:]

        return markerPoints.astype(int), im, success
    
    def _addRandomPoints(self, points, num, maxX=160, maxY=120):
        """
        This method adds specified numer of points to an array.

        Parameters
        ----------
        points: ndarray
            Array of points to which new ones should be appended. Each row holds point
            position (x, y)
        num: int
            Number of points that should be added to the given array.
        maxX: int
            Maximum posiible value of x coordinate.
        maxY: int
            Maximum posiible value of y coordinate.
        Returns
        ----------
        ndarray: Array with appended points.
        """
        addedPoints = np.zeros((num, 2))
        randX = np.random.randint(0, maxX, (num, 1))
        randY = np.random.randint(0, maxY, (num, 1))
        addedPoints[:,0] = randY.ravel()
        addedPoints[:,1] = randX.ravel()
        return np.append(points, addedPoints, axis=0)

    def _rotationVectRodriguesToEuler(self, rotVectRodrugies):
        tmpVect = np.zeros((3,))
        (rotationVectorPnPRod, _) = cv2.Rodrigues(rotVectRodrugies)
        # rotVectRodrugies = np.transpose(rotationVectorPnP)
        tmpVect[0] = math.atan2(rotationVectorPnPRod[0, 1], rotationVectorPnPRod[0, 0])
        tmpVect[1] = math.asin(-rotationVectorPnPRod[0, 2])
        tmpVect[2] = math.atan2(rotationVectorPnPRod[1, 2], rotationVectorPnPRod[2, 2])
        return tmpVect

    ################# OLD METHODS FOR STAR TRACKER INSPIRED ALGORITHM - CURRENTLY NOT USED #################
    def _calculateAnglePoints(self, p1x, p1y, p2x, p2y, p3x, p3y):
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

    def _getBlobAngles(self, centers, mode='All'):
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
            angles[i] = self._calculateAnglePoints(p1x, p1y, p2x, p2y, p3x, p3y)

        return 
    
    def _displayAlgorithmStages(self, images):
        tytul = "Algorytm przetwarzania obrazu 1"
        podtytuly = ["Obraz oryfinalny", "Progowanie", "Etykietowanie", "Usunięcie plam", "Centra plam", "Dodanie losowych punktów", "Camera Pose Estimation"]
        showImages(images, 3, 3, tytul, podtytuly)