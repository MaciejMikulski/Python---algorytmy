from visualAlgorithm import *

import numpy as np

visualAlg = visualAlgorithm(AlgorithmType.ALGORITHM_PEAK)

#cneters = np.array(((110, 77),
#                    (82,  83),
#                    (70,  61),
#                    (118, 57)), dtype=np.uint16)

cneters = np.array(((77, 110 ),
                    (83, 82 ),
                    (61, 70 ),
                    (57, 118 )), dtype=np.uint16)

(found_center, img, success) = visualAlg._findMarkerPoints(cneters, addRandPoints=False, randPointNum=0)

print(found_center)
print(success)