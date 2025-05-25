#include "find_marker_points.hpp"

inline float euclideanDistance(float x1, float y1, float x2, float y2) {
    float dx = x1 - x2;
    float dy = y1 - y2;
    return std::sqrt(dx * dx + dy * dy);
}

int findMarkerPoints(point_t *input_points, int blobNum, point_t *output_points)
{
    const float fourthBlobMaxDistanceError = 5.0f;
    int success = false;

    // Initialize output to (0,0)
    for (int i = 0; i < 4; ++i) {
        output_points[i].x = 0;
        output_points[i].y = 0;
    }

    if (blobNum < 4)
        return success;

    const int tripletNum = blobNum * (blobNum - 1) * (blobNum - 2);

    // Preallocate triplets and remaining point indices
    std::vector<std::array<int, 3>> pointTriplets(tripletNum);
    std::vector<std::vector<int>> otherPoints(tripletNum, std::vector<int>(blobNum - 3));

    int t = 0;
    for (int i = 0; i < blobNum; ++i) 
    {
        for (int j = 0; j < blobNum; ++j) 
        {
            for (int k = 0; k < blobNum; ++k) 
            {
                if (i != j && j != k && i != k) 
                {
                    pointTriplets[t] = {i, j, k};

                    int r = 0;
                    for (int m = 0; m < blobNum; ++m) 
                        if (m != i && m != j && m != k) 
                            otherPoints[t][r++] = m;

                    ++t;
                }
            }
        }
    }

    #ifdef DEBUG
        for (int i = 0; i < tripletNum; i++)
        {
            std::cout << "Triplet " << i << " ";
            std::cout << "(" << pointTriplets[i][0] << ", " << pointTriplets[i][1] << ", " << pointTriplets[i][2] << ") ";
            std::cout << "Other points ";
            std::cout << "(";
            for (int j = 0; j < blobNum-3; j++)
                std::cout << otherPoints[i][j] << ", ";
            std::cout << ")" << std::endl;
        }
    #endif

    float minDistance = std::numeric_limits<float>::max();
    int bestTripletIndex = -1;
    int bestOtherIndex = -1;

    for (int i = 0; i < tripletNum; ++i) 
    {
        const point_t& p0 = input_points[pointTriplets[i][0]];
        const point_t& p1 = input_points[pointTriplets[i][1]];
        const point_t& p2 = input_points[pointTriplets[i][2]];

        float v0x = static_cast<float>(p1.x - p0.x);
        float v0y = static_cast<float>(p1.y - p0.y);
        float v1x = static_cast<float>(p2.x - p1.x);
        float v1y = static_cast<float>(p2.y - p1.y);

        float predX = static_cast<float>(p0.x) + 0.5f * (v1x - v0x);
        float predY = static_cast<float>(p0.y) + 0.5f * (v1y - v0y);

        float cross = v0y * v1x - v0x * v1y;

        #ifdef DEBUG
            std::cout << "Triplet " << i << " ";
            std::cout << "Vectors (" << v0x << ", " << v0y << ", " << v1x << ", " << v1y << ") ";
            std::cout << "Prediction (" << predX << ", " << predY << ") ";
            std::cout << "Cross " << cross << ", ";
            std::cout << "Min dist " << minDistance << std::endl;
        #endif
        if (cross <= 0.0f)
            continue;  // Discard mirrored marker

        for (int j = 0; j < blobNum - 3; ++j) 
        {
            const point_t& candidate = input_points[otherPoints[i][j]];
            float dist = euclideanDistance(predX, predY, static_cast<float>(candidate.x), static_cast<float>(candidate.y));

            if (dist < fourthBlobMaxDistanceError && dist < minDistance) 
            {
                minDistance = dist;
                bestTripletIndex = i;
                bestOtherIndex = j;
                success = true;
            }
        }
    }

    if (success) 
    {
        output_points[0] = input_points[pointTriplets[bestTripletIndex][0]];
        output_points[1] = input_points[pointTriplets[bestTripletIndex][1]];
        output_points[2] = input_points[pointTriplets[bestTripletIndex][2]];
        output_points[3] = input_points[otherPoints[bestTripletIndex][bestOtherIndex]];
    }

    return success;
}

int find_marker_points(point_t *input_points, unsigned int blobNum, point_t *output_points)
{
    double fourthBlobMaxDistanceError = 5.0;
    double eps = 0.1; // For double comparison

    int success = 1;

    unsigned int tripletNum = blobNum * (blobNum - 1) * (blobNum - 2);

    std::vector<std::vector<unsigned int>> pointTriplets(tripletNum, std::vector<unsigned int>(3));
    // Store indexes of other points to use them in checking which one may fit the vector base
    std::vector<std::vector<unsigned int>> otherPoints(tripletNum, std::vector<unsigned int>(blobNum-3));

    unsigned int cnt = 0;


    for (unsigned int i = 0; i < blobNum; i++)
        for (unsigned int j = 0; j < blobNum; j++)
            for (unsigned int k = 0; k < blobNum; k++)
                if (i != j && j != k && i != k)
                {
                    pointTriplets[cnt][0] = i;
                    pointTriplets[cnt][1] = j;
                    pointTriplets[cnt][2] = k;

                    // Store all blob numbers that are not current i, j, k
                    unsigned int otherPointsIndex = 0;
                    for (unsigned int n = 0; n < blobNum; n++)
                        if (n != i && n != j && n != k)
                        {
                            otherPoints[cnt][otherPointsIndex] = n;
                            otherPointsIndex++;
                        }
                    cnt++;
                }

    // Calculate predicted placement of fourth point
    std::vector<std::vector<double>>    expectedP3(tripletNum, std::vector<double>(2));
    std::vector<std::vector<double>>   distanceErr(tripletNum, std::vector<double>(blobNum-3));
    std::vector<double>              crossProducts(tripletNum);
    
    point_t p0, p1, p2;
    point_t v0, v1;

    double minDistErr = 100000.0;

    for (unsigned int i = 0; i < tripletNum; i++)
    {
        // Get coordinates of points from triplet triplets
        p0 = input_points[pointTriplets[i][0]];
        p1 = input_points[pointTriplets[i][1]];
        p2 = input_points[pointTriplets[i][2]];

        // Calculate base vectors
        v0.x = p1.x - p0.x;
        v0.y = p1.y - p0.y;
        v1.x = p2.x - p1.x;
        v1.y = p2.y - p1.y;

        expectedP3[i][0] = (double)(p0.x) + 0.5 * (double)(v1.x - v0.x);
        expectedP3[i][1] = (double)(p0.y) + 0.5 * (double)(v1.y - v0.y);

        // Check for correct orientation of base vectors
        crossProducts[i] = (double)v0.x*(double)v1.y - (double)v0.y*(double)v1.x;

        // Calculate distance of predicted points to all other (not in triplet) points
        for (unsigned int j = 0; j < (blobNum-3); j++)
        {
            distanceErr[i][j] = sqrt(pow((double)(expectedP3[i][0]-(double)input_points[otherPoints[i][j]].x), 2.0) + 
                                     pow((double)(expectedP3[i][1]-(double)input_points[otherPoints[i][j]].y), 2.0));

            // Find lowest distance error
            if (distanceErr[i][j] < minDistErr)
                minDistErr = distanceErr[i][j];
        }
    }
    
    if (minDistErr >= fourthBlobMaxDistanceError)
        return success; // No distance is smaller than requested minumum error. Return failure.
    else
        success = 0;

    // Find the indices of all occurrences of the minimum value
    std::vector<std::vector<int>> indices(tripletNum, std::vector<int>(blobNum-3));

    for (int i = 0; i < (int)tripletNum; i++)
        for (int j = 0; j < (int)blobNum-3; j++)
            if (distanceErr[i][j] - minDistErr < eps) // double comparison with eps
                indices[i][j] = i;
            else
                indices[i][j] = -1;

    // Perform final selection of marker points
    for (unsigned int i = 0; i < tripletNum; i++)
        if (indices[i][0] >= 0)
            if (crossProducts[indices[i][0]] < 0.0) // Discad mirror view of the marker
            {
                output_points[0].x = input_points[pointTriplets[indices[i][0]][0]].x;
                output_points[0].y = input_points[pointTriplets[indices[i][0]][0]].y;
                output_points[1].x = input_points[pointTriplets[indices[i][0]][1]].x;
                output_points[1].y = input_points[pointTriplets[indices[i][0]][1]].y;
                output_points[2].x = input_points[pointTriplets[indices[i][0]][2]].x;
                output_points[2].y = input_points[pointTriplets[indices[i][0]][2]].y;
                output_points[3].x = input_points[otherPoints  [indices[i][0]][0]].x;
                output_points[3].y = input_points[otherPoints  [indices[i][0]][0]].y;
            }

    return success;
}

int find_marker_points_vitis(point_t *input_points, unsigned int blobNum, point_t *output_points)
{
    double fourthBlobMaxDistanceError = 5.0;
    double eps = 0.1; // For double comparison

    int success = 1;

    unsigned int tripletNum = blobNum * (blobNum - 1) * (blobNum - 2);

    std::vector<std::vector<unsigned int>> pointTriplets(tripletNum, std::vector<unsigned int>(3));
    // Store indexes of other points to use them in checking which one may fit the vector base
    std::vector<std::vector<unsigned int>> otherPoints(tripletNum, std::vector<unsigned int>(blobNum-3));

    unsigned int cnt = 0;


    for (unsigned int i = 0; i < blobNum; i++)
        for (unsigned int j = 0; j < blobNum; j++)
            for (unsigned int k = 0; k < blobNum; k++)
                if (i != j && j != k && i != k)
                {
                    pointTriplets[cnt][0] = i;
                    pointTriplets[cnt][1] = j;
                    pointTriplets[cnt][2] = k;

                    // Store all blob numbers that are not current i, j, k
                    unsigned int otherPointsIndex = 0;
                    for (unsigned int n = 0; n < blobNum; n++)
                        if (n != i && n != j && n != k)
                        {
                            otherPoints[cnt][otherPointsIndex] = n;
                            otherPointsIndex++;
                        }
                    cnt++;
                }

    // Calculate predicted placement of fourth point
    std::vector<std::vector<double>>    expectedP3(tripletNum, std::vector<double>(2));
    std::vector<std::vector<double>>   distanceErr(tripletNum, std::vector<double>(blobNum-3));
    std::vector<double>              crossProducts(tripletNum);
    
    point_t p0, p1, p2;
    point_t v0, v1;

    double minDistErr =  std::numeric_limits<double>::max();
    double tmp;
    for (unsigned int i = 0; i < tripletNum; i++)
    {
        // Get coordinates of points from triplet triplets
        p0 = input_points[pointTriplets[i][0]];
        p1 = input_points[pointTriplets[i][1]];
        p2 = input_points[pointTriplets[i][2]];

        // Calculate base vectors
        v0.x = p1.x - p0.x;
        v0.y = p1.y - p0.y;
        v1.x = p2.x - p1.x;
        v1.y = p2.y - p1.y;

        expectedP3[i][0] = (double)(p0.x) + 0.5 * (double)(v1.x - v0.x);
        expectedP3[i][1] = (double)(p0.y) + 0.5 * (double)(v1.y - v0.y);

        // Check for correct orientation of base vectors
        tmp = (double)v0.y*(double)v1.x - (double)v0.x*(double)v1.y;
        crossProducts[i] = tmp;

        // Calculate distance of predicted points to all other (not in triplet) points
        for (unsigned int j = 0; j < (blobNum-3); j++)
        {
            distanceErr[i][j] = sqrt(pow((double)(expectedP3[i][0]-(double)input_points[otherPoints[i][j]].x), 2.0) + 
                                     pow((double)(expectedP3[i][1]-(double)input_points[otherPoints[i][j]].y), 2.0));

            // Find lowest distance error
            if (distanceErr[i][j] < minDistErr)
                minDistErr = distanceErr[i][j];
        }
    }
    
    std::vector<std::vector<int>> indices(tripletNum, std::vector<int>(blobNum-3));

    if (minDistErr < fourthBlobMaxDistanceError) {
        // Step 3: Collect all (i,j) pairs with min error
        for (int i = 0; i < (int)tripletNum; i++) {
            for (int j = 0; j < (int)(blobNum-3); j++) {
                if (std::abs(distanceErr[i][j] - minDistErr) < 1e-6f) {
                    indices.emplace_back(i, j);
                }
            }
        }
        success = true;
    } else {
        // Early return if you're in a function returning multiple outputs
        return success;
    }

    /*
    if (minDistErr >= fourthBlobMaxDistanceError)
        return success; // No distance is smaller than requested minumum error. Return failure.
    else
        success = 0;

    // Find the indices of all occurrences of the minimum value
    std::vector<std::vector<int>> indices(tripletNum, std::vector<int>(blobNum-3));

    for (int i = 0; i < (int)tripletNum; i++)
        for (int j = 0; j < (int)blobNum-3; j++)
            if (std::abs(distanceErr[i][j] - minDistErr) < eps) // double comparison with eps
                indices[i][j] = i;
            else
                indices[i][j] = -1;
*/
    // Perform final selection of marker points
    for (unsigned int i = 0; i < tripletNum; i++)
        if (indices[i][0] >= 0)
            if (crossProducts[indices[i][0]] > 0.0) // Discad mirror view of the marker
            {
                output_points[0].x = input_points[pointTriplets[indices[i][0]][0]].x;
                output_points[0].y = input_points[pointTriplets[indices[i][0]][0]].y;
                output_points[1].x = input_points[pointTriplets[indices[i][0]][1]].x;
                output_points[1].y = input_points[pointTriplets[indices[i][0]][1]].y;
                output_points[2].x = input_points[pointTriplets[indices[i][0]][2]].x;
                output_points[2].y = input_points[pointTriplets[indices[i][0]][2]].y;
                output_points[3].x = input_points[otherPoints  [indices[i][0]][0]].x;
                output_points[3].y = input_points[otherPoints  [indices[i][0]][0]].y;
            }

    return success;
}

