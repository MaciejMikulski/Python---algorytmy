import glob
import os
import re
from typing import List

#This script fixes labels of the images which had incorrect distance values

imPaths = glob.glob(os.path.join(".", '*.'+str('png')))
print(imPaths[0])
for i in range(len(imPaths)):
    tmp = imPaths[i]
    tmpIns = tmp[:4] + '5' + tmp[(4):]
    print(tmpIns)
    os.rename(imPaths[i], tmpIns)


