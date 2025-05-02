#include <iostream>

#include <stdint.h>
#include <cstdlib>
#include <cmath>
#include <vector>
//#define tripletNum 336
//#define blobNum    8
#define blobNumber   8

typedef struct{
    int x;
    int y;
} point_t;

point_t in_points[blobNumber];
point_t out_points[4];

int find_marker_points(point_t *input_points, unsigned int blobNum, point_t *output_points);
//int find_marker_points(point_t *input_points, point_t *output_points);

int main()
{
    std::cout << "Input" << std::endl;
    in_points[0].x = 72;
    in_points[0].y = 42;
    in_points[1].x = 37;
    in_points[1].y = 87;
    in_points[2].x = 61;
    in_points[2].y = 92;
    in_points[3].x = 91;
    in_points[3].y = 71;
    in_points[4].x = 41;
    in_points[4].y = 107;
    in_points[5].x = 94;
    in_points[5].y = 100;
    in_points[6].x = 22;
    in_points[6].y = 43;
    in_points[7].x = 113;
    in_points[7].y = 3;
    /*
    for (int i = 4; i < 6; i++)
    {
        in_points[i].x = rand() % 160;
        in_points[i].y = rand() % 120;
        std::cout << i << ") X: " << in_points[i].x << " Y: " << in_points[i].y << std::endl;
    }
*/
    int ret = find_marker_points(in_points, blobNumber, out_points);

    std::cout << "Output" << std::endl;
    if (ret)
        std::cout << "No marker found" << std::endl;
    else
    {
        std::cout << "Marker found" << std::endl;
        for (int i = 0; i < 4; i++)
        {
            std::cout << i << ") X: " << out_points[i].x << " Y: " << out_points[i].y << std::endl;
        }
    }

    return ret;
}

int find_marker_points(point_t *input_points, unsigned int blobNum, point_t *output_points)
{
    float fourthBlobMaxDistanceError = 5.0;
    float eps = 0.1; // For float comparison

    int success = 1;

    unsigned int tripletNum = blobNum * (blobNum - 1) * (blobNum - 2);

    std::vector<std::vector<unsigned int>> pointTriplets(tripletNum, std::vector<unsigned int>(3));
    // Store indexes of other points to use them in checking which one may fit the vector base
    std::vector<std::vector<unsigned int>> otherPoints(tripletNum, std::vector<unsigned int>(blobNum-3));
    //unsigned int otherPoints[tripletNum][blobNum-3];
    unsigned int cnt = 0;

    //unsigned int possibleIndexes[blobNum];

    //for (unsigned int i = 0; i < blobNum; i++)
    //    possibleIndexes[i] = i;

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
    
    std::vector<std::vector<float>>    expectedP3(tripletNum, std::vector<float>(2));
    std::vector<std::vector<float>>   distanceErr(tripletNum, std::vector<float>(blobNum-3));
    std::vector<float>              crossProducts(tripletNum);
    //float    expectedP3[tripletNum][2];
    //float   distanceErr[tripletNum][blobNum-3];
    //float crossProducts[tripletNum];
    
    point_t p0, p1, p2;
    point_t v0, v1;
    point_t pa, pb;

    float minDistErr = 100000.0;

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

        expectedP3[i][0] = (float)(p0.x) + 0.5 * (float)(v1.x - v0.x);
        expectedP3[i][1] = (float)(p0.y) + 0.5 * (float)(v1.y - v0.y);

        // Check for correct orientation of base vectors
        crossProducts[i] = (float)v0.x*(float)v1.y - (float)v0.y*(float)v1.x;

        // Calculate distance of predicted points to all other (not in triplet) points
        for (unsigned int j = 0; j < (blobNum-3); j++)
        {
            pa.x = expectedP3[i][0];
            pa.y = expectedP3[i][1];
            pb.x = input_points[otherPoints[i][j]].x;
            pb.y = input_points[otherPoints[i][j]].y;
            distanceErr[i][j] = sqrt(pow((float)(pa.x-pb.x), 2.0) + pow((float)(pa.y-pb.y), 2.0));

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
    //int indices[tripletNum][blobNum-3];

    for (int i = 0; i < (int)tripletNum; i++)
        for (int j = 0; j < (int)blobNum-3; j++)
            if (distanceErr[i][j] - minDistErr < eps) // Float comparison with eps
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

/*
int find_marker_points(point_t *input_points, point_t *output_points)
{
    float fourthBlobMaxDistanceError = 5.0;
    float eps = 0.1; // For float comparison

    int success = 1;


    unsigned int pointTriplets[tripletNum][3];
    // Store indexes of other points to use them in checking which one may fit the vector base
    unsigned int otherPoints[tripletNum][blobNum-3];
    unsigned int cnt = 0;

    unsigned int possibleIndexes[blobNum];

    for (unsigned int i = 0; i < blobNum; i++)
        possibleIndexes[i] = i;

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
    float    expectedP3[tripletNum][2];
    float   distanceErr[tripletNum][blobNum-3];
    float crossProducts[tripletNum];
    
    point_t p0, p1, p2;
    point_t v0, v1;
    point_t pa, pb;

    float minDistErr = 100000.0;

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

        expectedP3[i][0] = (float)(p0.x) + 0.5 * (float)(v1.x - v0.x);
        expectedP3[i][1] = (float)(p0.y) + 0.5 * (float)(v1.y - v0.y);

        // Check for correct orientation of base vectors
        crossProducts[i] = (float)v0.x*(float)v1.y - (float)v0.y*(float)v1.x;

        // Calculate distance of predicted points to all other (not in triplet) points
        for (unsigned int j = 0; j < (blobNum-3); j++)
        {
            pa.x = expectedP3[i][0];
            pa.y = expectedP3[i][1];
            pb.x = input_points[otherPoints[i][j]].x;
            pb.y = input_points[otherPoints[i][j]].y;
            distanceErr[i][j] = sqrt(pow((float)(pa.x-pb.x), 2.0) + pow((float)(pa.y-pb.y), 2.0));

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
    int indices[tripletNum][blobNum-3];

    for (int i = 0; i < tripletNum; i++)
        for (int j = 0; j < blobNum-3; j++)
            if (distanceErr[i][j] - minDistErr < eps) // Float comparison with eps
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
*/

/*
int find_marker_points(point_t *input_points, unsigned int blobNum, point_t *output_points)
{
    float fourthBlobMaxDistanceError = 5.0;
    float eps = 0.1; // For float comparison

    int success = 1;

    unsigned int tripletNum = blobNum * (blobNum * blobNum - 3 * blobNum + 2);// n * (n-1) * (n-2);

    unsigned int *pointTriplets = new unsigned int[tripletNum * 3];
    // Store indexes of other points to use them in checking which one may fit the vector base
    unsigned int *otherPoints = new unsigned int[tripletNum * (blobNum-3)];
    unsigned int cnt = 0;

    unsigned int *possibleIndexes = new unsigned int[blobNum];
    for (unsigned int i = 0; i < blobNum; i++)
        possibleIndexes[i] = i;

    for (unsigned int i = 0; i < blobNum; i++)
    {
        for (unsigned int j = 0; j < blobNum; j++)
        {
            for (unsigned int k = 0; k < blobNum; k++)
            {
                if (i != j && j != k && i != k)
                {
                    pointTriplets[cnt*3 + 0] = i;
                    pointTriplets[cnt*3 + 1] = j;
                    pointTriplets[cnt*3 + 2] = k;

                    // Store all blob numbers that are not current i, j, k
                    unsigned int otherPointsIndex = 0;
                    for (unsigned int n = 0; n < blobNum; n++)
                    {  
                        if (n != i && n != j && n != k)
                        {
                            otherPoints[cnt*(blobNum-3) + otherPointsIndex] = n;
                            otherPointsIndex++;
                        }
                    }
                    cnt++;
                }
            }
        }
    }

    // Calculate predicted placement of fourth point
    float *expectedP3 = new float[tripletNum*2];
    float *distanceErr = new float[tripletNum * (blobNum-3)];
    float *crossProducts = new float[tripletNum];
    
    point_t p0, p1, p2;
    point_t v0, v1;
    point_t pa, pb;

    float minDistErr = 100000.0;

    for (unsigned int i = 0; i < tripletNum; i++)
    {
        // Get coordinates of points from triplet triplets
        p0 = input_points[pointTriplets[tripletNum*i+0]];
        p1 = input_points[pointTriplets[tripletNum*i+1]];
        p2 = input_points[pointTriplets[tripletNum*i+2]];

        // Calculate base vectors
        v0.x = p1.x - p0.x;
        v0.y = p1.y - p0.y;
        v1.x = p2.x - p1.x;
        v1.y = p2.y - p1.y;

        expectedP3[i*2+0] = (float)(p0.x) + 0.5 * (float)(v1.x - v0.x);
        expectedP3[i*2+1] = (float)(p0.y) + 0.5 * (float)(v1.y - v0.y);

        // Check for correct orientation of base vectors
        crossProducts[i] = (float)v0.x*(float)v1.y - (float)v0.y*(float)v1.x;

        // Calculate distance of predicted points to all other (not in triplet) points
        for (unsigned int j = 0; j < (blobNum-3); j++)
        {
            pa.x = expectedP3[i*2+0];
            pa.y = expectedP3[i*2+1];
            pb.x = input_points[otherPoints[i*tripletNum+j]].x;
            pb.y = input_points[otherPoints[i*tripletNum+j]].y;
            distanceErr[i*tripletNum+j] = sqrt(pow((float)(pa.x-pb.x), 2.0) + pow((float)(pa.y-pb.y), 2.0));

            // Find lowest distance error
            if (distanceErr[i*tripletNum+j] < minDistErr)
                minDistErr = distanceErr[i*tripletNum+j];
        }
    }
    
    if (minDistErr >= fourthBlobMaxDistanceError)
        return success; // No distance is smaller than requested minumum error. Return failure.
    else
        success = 0;

    // Find the indices of all occurrences of the minimum value
    unsigned int minDistErrCnt = 0; // Number of indices with minimum distanceError
    unsigned int *indices = new unsigned int[tripletNum * (blobNum-3)];

    for (unsigned int i = 0; i < tripletNum * (blobNum-3); i++)
        if (distanceErr[i] - minDistErr < eps) // Float comparison with eps
        {
            indices[minDistErrCnt] = i;
            minDistErrCnt++;
        }

    // Perform final selection of marker points
    for (unsigned int i = 0; i < tripletNum; i++)
        if (crossProducts[indices[i % (blobNum-3)]] < 0.0) // Discad mirror view of the marker
        {
            output_points[0].x = input_points[pointTriplets[indices[i % (blobNum-3)]+0]].x;
            output_points[0].y = input_points[pointTriplets[indices[i % (blobNum-3)]+0]].y;
            output_points[1].x = input_points[pointTriplets[indices[i % (blobNum-3)]+1]].x;
            output_points[1].y = input_points[pointTriplets[indices[i % (blobNum-3)]+1]].y;
            output_points[2].x = input_points[pointTriplets[indices[i % (blobNum-3)]+2]].x;
            output_points[2].y = input_points[pointTriplets[indices[i % (blobNum-3)]+2]].y;
            output_points[3].x = input_points[otherPoints  [indices[i % (blobNum-3)]+0]].x;
            output_points[3].y = input_points[otherPoints  [indices[i % (blobNum-3)]+0]].y;
        }

    delete indices;
    delete expectedP3;
    delete distanceErr;
    delete crossProducts;
    delete possibleIndexes;   
    delete otherPoints;
    delete pointTriplets;

    return success;
}
*/