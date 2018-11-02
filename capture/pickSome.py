

import pymysql
import pandas as pd
import sys

if len(sys.argv) != 2:
    print("please provide the number of capture you want to do\naborting")
    sys.exit(1)


nb_capt = int(sys.argv[1])

try :
    connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    ground_truth = pd.read_sql("SELECT * FROM `ubuntu_cleaned_packets` ",connection)

    connection.close()
    print("Loading from db")

except Exception as e:

    print("{}\n loading from CSV Files".format(e))

    try :
        ground_truth = pd.read_csv("../attack/cleaned_and_expanded_gt.csv")

    except:
        print("Cannot find cleaned_and_expanded_gtAll.csv in the attack dir. or \nCannot find ubuntu_captures.csv in capture dir.\naborting")
        sys.exit(1)



ground_truth = ground_truth.set_index("id")


to_capture = ground_truth[["Package", "Version", "Summing dependances"]].sample(nb_capt)

print("Ready to capture \n", to_capture)

# We only extract the useful columns
to_capture.to_csv("package.txt", header =False)
