#!/usr/bin/python3

import pandas as pd
import sys
import pymysql
sys.path.append("../utils/")
from fputils import load_fingerpatch
from tqdm import tqdm # For progression bar
tqdm.pandas()

###################### Globals ######################

EXTRA_SIZE_AVERAGE = 283   # Made from stats about captured packets
EXTRA_SIZE_VARIATION = 5
TOP_K_CONSIDERATION = 15
M = "Recommends"
useOldCapture = False      # By default the matching is done without taking into account old captures
update_gt = False

if len(sys.argv) == 2 :
    useOldCapture = True




###################### Functions ######################

def remove_dependencies_in_dest(sources, dest, df, m):
    """
    return  sets of dependences that are already instaled in the victime's machine

    sources: list of indexes of packages that the victim has already installed
    dest :   specific targeted pack
    """
    s = set()
    for source in sources:
        tmp = df.loc[source][m+"_Childrens"]
        #print(frozenset(tmp))
        s = s.union(tmp)

    if dest == 5529:
        print( len(s))
        print(len(df.loc[dest][m+"_Childrens"]))



    return df.loc[dest][m+"_Childrens"].intersection(s)


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

def distance_from_expected_average_size_with_state_summing(x, size_to_match):

    return abs(size_to_match - x["State_Summing"] - (EXTRA_SIZE_AVERAGE * len(x["State_Childrens"])))

# When matching with Size
def distance_from_expected_average_size_with_summing(x, size_to_match, m):
    return abs(size_to_match - x[m+"_Summing"] - (EXTRA_SIZE_AVERAGE * x[m +"_Elements_involved"]))


def distance_from_expected_average_size(x, alreadyCaptured, size_to_match, gt, m):
    """
    distance_from_expected_average_size: estimate the size a specific package index x
                                         has to match by taking into account the packages that
                                         has already been installed by the victim.
    """


    dependencesToNotTakeIntoAccount = remove_dependencies_in_dest(alreadyCaptured, x.name, gt)
    #print(dependencesToTakeIntoAccount)
    toSubstract = 0
    for d in dependencesToNotTakeIntoAccount:
        toSubstract += gt.loc[d]["Size"]

    if x.name == 5529:
        print("#Offset : ", len(x[M+"_Childrens"]) - len(dependencesToNotTakeIntoAccount))
        print(abs(size_to_match - (x[M+"_Summing"] - toSubstract) - (EXTRA_SIZE_AVERAGE * (len(x[M+"_Childrens"]) - len(dependencesToNotTakeIntoAccount)))))

    return abs(size_to_match - (x[M+"_Summing"] - toSubstract) - (EXTRA_SIZE_AVERAGE * (len(x[M+"_Childrens"]) - len(dependencesToNotTakeIntoAccount))))

def distance_from_expected_average_size_after_reducing_children(x, size_to_match, gt):
    summing = 0

    # Summing all packages the victim has to download according to the current state,
    for c in x[M+"_Childrens"]:
        summing += gt.loc[c]["Size"]

    return abs(size_to_match - summing - (EXTRA_SIZE_AVERAGE * len(x[M+"_Childrens"])))

def state_summing(x, gt):
    summing = 0
    # Summing all packages the victim has to download according to the current state,
    for c in x[M+"_Childrens"]:
        summing += gt.loc[c]["Size"]

    return summing


def reduce_childrens(x, downloaded):
    s = x["State_Childrens"]
    for d in downloaded.copy():
        if d in  s:
            s.remove(d)
    return s



###################### INIT ######################

print("Loading attack_table")
attack_table = load_fingerpatch("ubuntu_captures")

attack_table = attack_table[attack_table["Processed"] == 0] # Only look at newly captured packages

if len(attack_table) == 0:
    print("Nothing to match")
    sys.exit(0)


print("Loading gt")
gt = load_fingerpatch("ubuntu_cleaned_packets", parse_children="Recommends")

# Partion the package in two groups: im_ => the packages that have been alreadySeen
downloaded = gt[gt["in"] == 1]

gt["State_Childrens"] = gt[M + "_Childrens"]
gt["State_Summing"] = gt[M + "_Summing"]
if useOldCapture:
    print("Reduce childrens and compute state_summing")
    gt["State_Childrens"] = gt.progress_apply(lambda x: reduce_childrens(x, downloaded.index.tolist()), axis = 1)
    gt = gt[gt["in"] == 0]
    gt["State_Summing"] = gt.progress_apply(lambda x: state_summing(x, gt), axis = 1)



####################### MAIN ######################


# Matching using http
attack_table["HTTP_Match"] = attack_table["HTTP_Seq"].map(lambda x: matchHTTP(x, gt))

tot = len(attack_table)
# Matching Using Size

for capture_id, row in attack_table.iterrows():
    if row["nb_flows"] == 0 :
        print("Captured tempered, skipping")
        continue

    print("--Matching capture id = ", capture_id, "--")

    # Use a temporary gt because we want to be flexible and switch the state of the victim across captures
    tmp_gt = gt
    captured_size = sum(row['Payload_received'])
    already_captured = row["already_captured"]

    # updating state
    if len(already_captured) != 0:
        already_captured = eval(already_captured)

        # The childrens are also captured
        already_captured = list(tmp_gt.loc[already_captured]["State_Childrens"])
        print("Adapte to new state already captured: ", already_captured )
        tmp_gt["State_Childrens"] = tmp_gt.progress_apply(lambda x: reduce_childrens(x, already_captured), axis = 1)

        print("Dropping ", already_captured)
        tmp_gt = tmp_gt.drop(already_captured)
        tmp_gt["State_Summing"] = tmp_gt.progress_apply(lambda x: state_summing(x, tmp_gt), axis = 1)






    tmp_gt["dist_from_expected_size"] = tmp_gt.progress_apply(lambda x: distance_from_expected_average_size_with_state_summing(x, captured_size ), axis = 1)

    """
    if useOldCapture :

        gt["dist_from_expected_size"] = gt.progress_apply(lambda x: distance_from_expected_average_size_after_reducing_children(x, captured_size, gt), axis = 1)

        #gt["dist_from_expected_size"] = gt.progress_apply(lambda x: distance_from_expected_average_size(x, in_.index.tolist(), captured_size, gt, M ), axis = 1)
    else :
        gt["dist_from_expected_size"] = gt.progress_apply(lambda x: distance_from_expected_average_size_with_summing(x, captured_size ), axis = 1)

    """
    result = tmp_gt.sort_values(by="dist_from_expected_size").head(TOP_K_CONSIDERATION)

    http_succeed = False
    size_succeed = False

    http_found = []
    size_found = []



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
    ranking=-1
    for i, (id , r) in enumerate(result.iterrows()):

        if id == row["truth_id"]:
            print("  SIZE | Matched found : in gt id = {} at position {} ".format( id, i))
            size_succeed = True
            ranking=i
            break

    if not size_succeed :
        print("  SIZE | No matched found : capture id = {} ->  ??? ".format(capture_id))

    # Commiting to the db
    sql = "UPDATE `ubuntu_captures` SET `Processed` = '1', `http_succeed` = '"+str(int(http_succeed))+"', `size_succeed` = '"+str(int(size_succeed))+"', `http_found` = '"+str(row["HTTP_Match"])+"', `size_found` = '"+str(result["dist_from_expected_size"].tolist())+"' , `size_ranking` = '"+str(ranking)+"' WHERE `ubuntu_captures`.`capture_id` = %s;"

    print("\n"+sql+"\n")

    # Here we could set in_ to 1 in the gt since we think we got a capture
    # sql2 = ......


    try :
        connection = pymysql.connect(host='localhost',
                                 user='fingerpatch',
                                 password='fingerpatch',
                                 db='fingerpatch',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(sql, capture_id)
            # if size_succeed || http_succeed && update_gt :
            #
            connection.commit();



    except Exception as e:
        print(e)

print("Done")
