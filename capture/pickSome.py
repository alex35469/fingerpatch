

import pymysql
import pandas as pd
import sys
sys.path.append("../utils/")
from fputils import load_fingerpatch

DEP_NUM = -1
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("please provide the number of capture you want and/or the mode (N for no Dep Y for Dep) to do\naborting")
    sys.exit(1)


nb_capt = int(sys.argv[1])

if len(sys.argv) == 3:
    DEP_NUM = int(sys.argv[2])


print("Preparing {} packages to download, with NB_DEPENDS = {}\n in random_package.txt".format(nb_capt, DEP_NUM))


gt = load_fingerpatch("ubuntu_cleaned_packets")



if DEP_NUM >= 0:
    to_capture = gt[gt["Recommends_Elements_involved"] == DEP_NUM + 1]
    print("Picking {} from {} elements".format(nb_capt, len(to_capture)))
    to_capture = to_capture[["Package", "Version", "Recommends_Summing"]].sample(nb_capt)

else :
    print("Picking {} from {} elements".format(nb_capt, len(gt)))
    to_capture = gt[["Package", "Version", "Recommends_Summing"]].sample(nb_capt)



print("Ready to capture \n", to_capture)

# We only extract the useful columns
to_capture.to_csv("random_package.txt", header =False)
