#include <stdint.h>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <limits>
#include <array>

#include <iostream>

#define DEBUG

#define blobNumber   6

typedef struct{
    int x;
    int y;
} point_t;

float euclideanDistance(float x1, float y1, float x2, float y2);
int findMarkerPoints(point_t *input_points, int blobNum, point_t *output_points);
int find_marker_points(point_t *input_points, unsigned int blobNum, point_t *output_points);
int find_marker_points_vitis(point_t *input_points, unsigned int blobNum, point_t *output_points);