import numpy as np
import math

def _findMarkerPoints(self, centers):
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

        bool indicating if the algorithm was successful. 
        """
        fourthBlobMaxDistanceError = 5.0
        markerPoints = np.zeros((4,2))
        success = False

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
            tmp  = np.cross(v0,v1)
            crossProducts[i] = tmp
            # Calculate distance of predicted points to all other (not in triplet) points
            for j in range(otherPoints.shape[1]):
                pa = expectedP3[i,:]
                pb = centers[otherPoints[i,j],:]
                distanceErr[i,j] = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)

        # TODO: add selection based on absolute value of min error and return if it is too big
        # Find the indices of all occurrences of the minimum value
        if np.min(distanceErr) < fourthBlobMaxDistanceError:
            indices = np.argwhere(distanceErr == np.min(distanceErr))
            success = True
        else:
            return markerPoints.astype(int), success

        # Perform final selection of marker points
        for i in range(indices.shape[0]):
            if crossProducts[indices[i,0]] < 0.0: # Discad mirror view of the marker
                markerPoints[0,:] = centers[pointTriplets[indices[i,0], 0],:]
                markerPoints[1,:] = centers[pointTriplets[indices[i,0], 1],:]
                markerPoints[2,:] = centers[pointTriplets[indices[i,0], 2],:]
                markerPoints[3,:] = centers[otherPoints  [indices[i,0], 0],:]

        return markerPoints.astype(int), success