#!/usr/bin/python3

import pandas as pd
import sys
import pymysql

###################### Globals ######################

EXTRA_SIZE_AVERAGE = 283   # Made from stats about captured packets
EXTRA_SIZE_VARIATION = 5
TOP_K_CONSIDERATION = 15


###################### Functions ######################

# Matching functions
# When matching with HTTP
def matchHTTP(x, df):
    """
    x String contraining the filename
    To use with a map on the attribute FileName
    """

    requests = x

    match = []

    for r in requests:
        s = r.split(" ")[1][8:]
        if len(s) < 20: # With only 20 character we reckon that the request doesn't contain enough information for a perfect match
            continue

        s = s.replace("%2b", "\+")
        found = df[df.Filename.str.contains(s)]
        match += found.index.tolist()

    # remove duplicates
    match = list(set(match))

    return match

# When matching with Size
def distance_from_expected_average_size(x, size_to_match):
    return abs(size_to_match - x["Summing dependances"] - (EXTRA_SIZE_AVERAGE * x["Elements involved"]))


###################### INIT ######################

# Trying to read the data from the fingerpatch db
# Or if it doesnt't work from the csv
try :
    connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    ground_truth = pd.read_sql("SELECT * FROM `ubuntu_cleaned_packets` ",connection)
    attack_table = pd.read_sql("SELECT * FROM `ubuntu_captures` ",connection)

    connection.close()
    print("Loading from db")

except Exception as e:

    print("{}\n loading from CSV Files".format(e))

    try :
        ground_truth = pd.read_csv("cleaned_and_expanded_gt.csv")
        attack_table = pd.read_csv("../capture/ubuntu_captures.csv")

    except:
        print("Cannot find cleaned_and_expanded_gt.csv in the attack dir. or \nCannot find ubuntu_captures.csv in capture dir.\naborting")
        sys.exit(1)


ground_truth = ground_truth.set_index("id")
ground_truth["Childrens"] = ground_truth['Childrens'].map(lambda x: eval(x))

attack_table = attack_table.set_index("capture_id")
attack_table = attack_table[attack_table["matched"] == 0] # Only look at newly captured packages
attack_table["Payload_received"] = attack_table["Payload_received"].map(lambda x : eval(x))




attack_table["HTTP_Seq"] = attack_table["HTTP_Seq"].map(lambda x : eval(x))

####################### MAIN ######################


# Matching using http
attack_table["Http Match"] = attack_table["HTTP_Seq"].map(lambda x: matchHTTP(x, ground_truth))

tot = len(attack_table)
# Matching Using Size

for capture_id, row in attack_table.iterrows():
    if row["nb_flows"] == 0 :
        print("Captured tempered, skipping")
        continue

    ground_truth["dist_from_expected_size"] = ground_truth.apply(lambda x: distance_from_expected_average_size(x, sum(row['Payload_received']) ), axis = 1)
    result = ground_truth.sort_values(by="dist_from_expected_size").head(TOP_K_CONSIDERATION)

    found_Size = False
    found_Http = False

    for r in row["Http Match"]:
        if r == row["truth_id"]:
            print("HTTP | Matched found #### CAPTURE INITIAL: capture id = {} -> ground_truth id = {}".format(capture_id, r ))
            found_Http =True
            continue

        print("HTTP | Matched found : capture id = {} -> ground_truth id = {} ".format(capture_id, r ))
        found_Http = True



    if not found_Http:
        print("HTTP | No matched found : capture id = {} ->  ??? ".format(capture_id))

    for i, (id , r) in enumerate(result.iterrows()):

        if id == row["truth_id"]:
            print("SIZE | Matched found : capture id = {} -> ground_truth id = {} at position {} ".format(capture_id, id, i))
            found_Size = True
            break

    if not found_Size :
        print("SIZE | No matched found : capture id = {} ->  ??? ".format(capture_id))

    # Commiting to the db
    sql = "UPDATE `ubuntu_captures` SET `matched` = '1' WHERE `ubuntu_captures`.`capture_id` = %s;"
    try :
        connection = pymysql.connect(host='localhost',
                                 user='fingerpatch',
                                 password='fingerpatch',
                                 db='fingerpatch',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(sql, capture_id)
            connection.commit();
    except Exception as e:
        print(e)

print("Done")
