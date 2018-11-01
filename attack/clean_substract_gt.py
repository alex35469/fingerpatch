
#
# Read raw db from that the crawler left to us
# Produce cleaned db (Remove duplactes and useless coloumns)
# Substract usefull relation not explicitly given by the
#


import sys
import pandas as pd
import pymysql
import tqdm

BUILD_WHOLE_TREE = False



########################## FUNCTIONS ####################


def computeSumOnDep(x, df):
    """
    x :
    Compute the high level sum of all the dependences that x needs
    """

    childrens = x["Childrens"]
    summingDep = 0

    # We include ourself in the children to count everything
    childrens.add(x.name)

    for c in childrens:
        summingDep += df.loc[c]["Size"]

    df.at[x.name,"Summing dependances"] = summingDep

    return summingDep


def recursiveSearchOnDep(x, df, alreadySeen):

    """
    x : The current data Serie, Assuming that x contains Package, Version, Depends, Size and
        Summing dependances, Dependance traces for the dynamic approach

    summing : The sum of the size in Bytes
    df is the db we are performing the recursive search
    alreadySeen : Dict with the already seen packages + version"""

    childrens = set()

    if x.name in alreadySeen:
        return childrens

    deps = parseAndFindDep(x["Depends"], df)
    childrens.add(x.name)

    if len(deps) == 0: # Touches the leaves

        df.at[x.name, "Childrens"] = childrens

        return childrens

    # Adding itself in the list of childrens

    alreadySeen.add(x.name)

    for dep in deps:


        newX = df.loc[dep]


        childrensChildren = newX["Childrens"]

        if len(childrensChildren) == 0:

            childrensChildren = recursiveSearchOnDep(newX, df, alreadySeen)



        #print("For ", dep, " we have childrens: ", childrensChildren)
        childrens = childrens.union(childrensChildren)
        childrens.add(dep)
        alreadySeen.add(dep)




    df.at[x.name, "Childrens"] = childrens


    return childrens





def parseAndFindDep(depString, df):
    """
    Return a list of ubuntu_packages id w.r.t the Dataframe df
        which represents the dependances in depString
    """
    ids = list()

    allPckg = df["Package"].unique()

    for d in depString.split(", "):


        for d2 in d.split(" | "):

            d2 = d2.split(" (")

            package = d2[0]

            #print(package)

            version = ""
            if len(d2) == 2:
                # We have more info about the version
                (req, version) = d2[1][:-1].split(" ")

                if req == "<<" :
                    req = "<"
                if req == ">>":
                    req = ">"
                if req == "=":
                    req = "=="


            if package in allPckg:

                # TOFIX simple string comparison doesn't work because 2.12.4 > 2.9.3
                package_candidates = df[df["Package"] == package].sort_values(by="Version", ascending=False)
                id_ = package_candidates.iloc[0].name

                if version != "":
                    # Restraint further more using the version spec.
                    package_candidates = package_candidates.query("Version "+req+" '"+version+"'")

                    if len(package_candidates) > 0 :
                        # just take the most recent one if there are many versions
                        id_ = package_candidates.iloc[0].name


                # Add it only if it's the first time we add it
                if id_ not in ids:
                    ids = ids + [id_]

                # We found it no need to take the packages after "|"
                break

    return ids


####################### INIT ######################

# Trying to read the data from the fingerpatch db
# Or if it doesnt't work from the csv
try :
    connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    ground_truth = pd.read_sql("SELECT * FROM `ubuntu_packets` ",connection)
    connection.close()
    print("Loading from db")

except :

    print("No db found, loading from CSV Files")

    try :
        ground_truth = pd.read_csv("../crawl/ubuntu_packets.csv")

    except:
        print("Cannot find ubuntu_packets.csv in the crawl dir. \naborting")
        sys.exit(1)


# CLEANING
ground_truth = ground_truth.set_index("id")

# Selecting only interessting fields i.e. the attacker has no mean to distinguish two packages that have the same size but different packageMode
ground_truth = ground_truth.drop_duplicates(['Package', 'Version', 'Size', 'Depends', 'Architecture'])


# Selecting only interessting columns
ground_truth = ground_truth.drop(axis= 1, columns=['capture_id','SHA1', 'Priority', 'Description-md5', 'MD5sum', 'SHA256', 'packageMode' ])

ground_truth = ground_truth.fillna("")

########### FOR TESTING #########
ground_truth = ground_truth[0:5000]
#################################


####################### MAIN ######################

ground_truth["#Depends"] = ground_truth["Depends"].map(lambda x: 0 if x == "" else len(x.split(",")))

# EXTRACT RELATION
ground_truth["Summing dependances"] = -1
ground_truth["Dependance traces"] = "{}"
ground_truth["Childrens"] = ""

ground_truth = ground_truth.sort_values(["#Depends"])

tot = len(ground_truth)

# For each entry, we extract all the dependences and build the tree if required
print("extracting dependences")
for _, row in tqdm.tqdm(ground_truth.iterrows(), total=tot):
    _ = recursiveSearchOnDep(row, ground_truth, set())

ground_truth["Elements involved"] = ground_truth['Childrens'].map(lambda x: len(x))
print("Elements involved per packages description: \n",ground_truth["Elements involved"].describe())

# For each entry we compute the high level of dependence
print("Summing dependances")
for _, row in tqdm.tqdm(ground_truth.iterrows(), total=tot ):
    summingDep = computeSumOnDep(row, ground_truth)
    ground_truth.at[row.name, "Summing dependances"] = summingDep

print("Summing dependances description: \n",ground_truth["Summing dependances"].describe())



# Add a columns Frequency to the db
print("Compute Frequence")
d = dict()
for _, row in tqdm.tqdm(ground_truth.iterrows(), total=tot ):


    d[row.name] = ground_truth["Childrens"].map(lambda childrens: row.name in childrens).sum()




s = pd.Series(d, name='Dependence Frequency')
ground_truth = ground_truth.assign( Frequency= s)

print("Frequence description: \n",ground_truth["Frequency"].describe())

# Compute Freq in %
ground_truth["Freq in %"] = ground_truth["Frequency"].map(lambda x : x/len(ground_truth) )



### SAVE RESULTS
try :
    connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    ground_truth = pd.read_sql("SELECT * FROM `ubuntu_packets` ",connection)
    connection.close()
    print("Saving in db : `cleaned_and_expanded_gt`")

except :

    "Couldn't commit to the db"

print("Saving cleaned_and_expanded_gt.csv ")
ground_truth[["Package", "Version", "Size","Elements involved", "Childrens", "Frequency" ,"Freq in %"]].to_csv("cleaned_and_expanded_gt_Final.csv")

print("Done")
