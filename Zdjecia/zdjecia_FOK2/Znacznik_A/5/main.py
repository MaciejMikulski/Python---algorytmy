import glob
import os
import re
from typing import List

#This script fixes labels of the images which had incorrect distance values

imPaths = glob.glob(os.path.join(".", '*.'+str('png')))

for i in range(len(imPaths)):
    tmp = imPaths[i]
    if tmp[4] == "4":
        tmp = tmp[:4] + tmp[(5):]
    os.rename(imPaths[i], tmp)


