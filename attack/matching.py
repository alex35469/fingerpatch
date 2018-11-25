#!/usr/bin/python3

import pandas as pd
import sys
import pymysql
sys.path.append("../utils/")
from fputils import load_fingerpatch

###################### Globals ######################

EXTRA_SIZE_AVERAGE = 283   # Made from stats about captured packets
EXTRA_SIZE_VARIATION = 5
TOP_K_CONSIDERATION = 15
M = "Recommends"


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
        found = df[df["Filename"] == r]
        match += found.index.tolist()

    # remove duplicates
    match = list(set(match))


    return match

# When matching with Size
def distance_from_expected_average_size(x, size_to_match, m):
    return abs(size_to_match - x[m+"_Summing"] - (EXTRA_SIZE_AVERAGE * x[m +"_Elements_involved"]))

###################### INIT ######################



print("Loading gt")
gt = load_fingerpatch("ubuntu_cleaned_packets", parse_children=False)

print("Loading attack_table")
attack_table = load_fingerpatch("ubuntu_captures")

#attack_table = attack_table[attack_table["Processed"] == 0] # Only look at newly captured packages

####################### MAIN ######################


# Matching using http
attack_table["HTTP_Match"] = attack_table["HTTP_Seq"].map(lambda x: matchHTTP(x, gt))

tot = len(attack_table)
# Matching Using Size

for capture_id, row in attack_table.iterrows():
    if row["nb_flows"] == 0 :
        print("Captured tempered, skipping")
        continue

    gt["dist_from_expected_size"] = gt.apply(lambda x: distance_from_expected_average_size(x, sum(row['Payload_received']), M ), axis = 1)
    result = gt.sort_values(by="dist_from_expected_size").head(TOP_K_CONSIDERATION)

    http_succeed = False
    size_succeed = False

    http_found = []
    size_found = []


    print("--Matching capture id = ", capture_id, "--")
    for r in row["HTTP_Match"]:
        if r == row["truth_id"]:
            print("  HTTP | Matched found #### CAPTURE INITIAL:  gt id = {}".format( r ))
            http_succeed =True
            continue

        print("  HTTP | Matched found in gt: id = {} ".format( r ))

    print("# {}/{} HTTP request found".format(len(attack_table.loc[capture_id]["HTTP_Match"]), len(attack_table.loc[capture_id]["HTTP_Seq"])))

    if not http_succeed:
        print("HTTP | No matched found : capture id = {} ->  ??? ".format(capture_id))

    print()
    for i, (id , r) in enumerate(result.iterrows()):

        if id == row["truth_id"]:
            print("  SIZE | Matched found : in gt id = {} at position {} ".format( id, i))
            size_succeed = True
            break

    if not size_succeed :
        print("  SIZE | No matched found : capture id = {} ->  ??? ".format(capture_id))

    # Commiting to the db
    sql = "UPDATE `ubuntu_captures` SET `Processed` = '1', `http_succeed` = '"+str(int(http_succeed))+"', `size_succeed` = '"+str(int(size_succeed))+"', `http_found` = '"+str(row["HTTP_Match"])+"', `size_found` = '"+str(result.index.tolist())+"' WHERE `ubuntu_captures`.`capture_id` = %s;"

    print("\n"+sql+"\n")


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
