#include "EPnP.hpp"
#include "EPnPRansacModel.hpp"
#include "Ransac.hpp"
#include "PoseUtil.hpp"

#include <algorithm>
#include <cstdlib>
#include <chrono>
#include <iterator>
#include <ctime>

namespace
{
    const double uc = 80;
    const double vc = 60;
    const double fu = 800;
    const double fv = 800;

    const int n = 4;
}

#include "find_marker_points.hpp"

point_t in_points[blobNumber];
point_t out_points[4];

bool pose_estimation_test(point_t *marker_points);

int main()
{
    std::cout << "Input" << std::endl;
    //in_points[0].x = 72;
    //in_points[0].y = 42;
    //in_points[1].x = 37;
    //in_points[1].y = 87;
    //in_points[2].x = 61;
    //in_points[2].y = 92;
    //in_points[3].x = 91;
    //in_points[3].y = 71;

    //in_points[0].x = 70;
    //in_points[0].y = 62;
    //in_points[1].x = 82;
    //in_points[1].y = 88;
    //in_points[2].x = 110;
    //in_points[2].y = 77;
    //in_points[3].x = 118;
    //in_points[3].y = 57;
    //in_points[4].x = 2;
    //in_points[4].y = 107;
    //in_points[5].x = 94;
    //in_points[5].y = 100;
    //in_points[6].x = 22;
    //in_points[6].y = 43;
    //in_points[7].x = 113;
    //in_points[7].y = 3;

    in_points[0].x = 58;
    in_points[0].y = 117;
    in_points[1].x = 58;
    in_points[1].y = 118;
    in_points[2].x = 61;
    in_points[2].y = 71;
    in_points[3].x = 78;
    in_points[3].y = 110;
    in_points[4].x = 88;
    in_points[4].y = 82;
    in_points[5].x = 88;
    in_points[5].y = 83;

    int ret = find_marker_points(in_points, blobNumber, out_points);
    std::cout << "Status: " << ret << "Old function points: " << std::endl;
    for (int i = 0; i < 4; i++)
        std::cout << "X: " << out_points[i].x << ", Y: " << out_points[i].y << std::endl;

    ret = find_marker_points_vitis(in_points, blobNumber, out_points);
    std::cout << "Status: " << ret << "Vitis function points: " << std::endl;
    for (int i = 0; i < 4; i++)
        std::cout << "X: " << out_points[i].x << ", Y: " << out_points[i].y << std::endl;

    ret = findMarkerPoints(in_points, blobNumber, out_points);
    std::cout << "Status: " << ret << "New function points: " << std::endl;
    for (int i = 0; i < 4; i++)
        std::cout << "X: " << out_points[i].x << ", Y: " << out_points[i].y << std::endl;

    pose_estimation_test(out_points);

    return ret;
}

bool pose_estimation_test(point_t *marker_points)
{
	using std::cout;
	using std::endl;
	cout << ">>>> Pose estimation test:" << endl;

	EPnP::epnp<double> PnP;

	PnP.set_internal_parameters(uc, vc, fu, fv);
	PnP.set_maximum_number_of_correspondences(n);

	PnP.reset_correspondences();

    PnP.add_correspondence( 2.0,  0.0, 0.0, marker_points[0].x, marker_points[0].y);
    PnP.add_correspondence( 0.0, -2.0, 0.0, marker_points[1].x, marker_points[1].y);
    PnP.add_correspondence(-2.0,  0.0, 0.0, marker_points[2].x, marker_points[2].y);
    PnP.add_correspondence( 2.0,  2.0, 0.0, marker_points[3].x, marker_points[3].y);

	//PnP.add_correspondence(-2.0, 0.0, 0.0, 70, 62);
    //PnP.add_correspondence(0.0, -2.0, 0.0, 82, 88);
    //PnP.add_correspondence(2.0,  0.0, 0.0, 110, 77);
    //PnP.add_correspondence(2.0,  2.0, 0.0, 118, 57);

	double R_est[3][3], t_est[3];
	double err2 = PnP.compute_pose(R_est, t_est);

	cout << ">>> Reprojection error: " << err2 << endl;
	cout << "Found pose:" << endl;
	PnP.print_pose(R_est, t_est);
	cout << endl;

	return true;
}