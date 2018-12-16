#!/usr/bin/python3

#
# Read raw db from that the crawler left to us
# Produce cleaned db (Remove duplactes and useless coloumns)
# Substract usefull relation not explicitly given by the
#


import sys
import pandas as pd
import pymysql
import gc
from tqdm import tqdm # For progression bar
tqdm.pandas()

# For parrallel
import dask.dataframe as dd
from dask.multiprocessing import get
from multiprocessing import cpu_count
from dask.diagnostics import ProgressBar



BUILD_WHOLE_TREE = False
CORES = cpu_count() #Number of CPU cores available
modes = ["Depends", "Recommends", "Suggests"] # Use to precise at which degree we want to seek of dependences
ss = [] #Used for storing data series of frequencies


########################## FUNCTIONS ####################
def computeSumOnDep(x, dicSize):
    """
    x : Compute the high level sum of all the dependences that x needs
    """
    summingDep = 0

    for c in x:
        summingDep += dicSize[c]

    return summingDep


def recursiveOnly(x, df, alreadySeen, mode="Depends"):

    """
    x : The current data Serie, Assuming that x contains Package, Version, Depends, Size and
        Summing dependances, Dependance traces for the dynamic approach

    summing : The sum of the size in Bytes
    df is the db we are performing the recursive search
    alreadySeen : Dict with the already seen packages + version"""

    childrens = set()

    if x.name in alreadySeen:
        return childrens

    deps = x["Depends_Parsed"]

    if mode == "Recommends":
        deps = deps.union(x["Recommends_Parsed"])

    if mode == "Suggests":
        deps = deps.union(x["Recommends_Parsed"])
        deps = deps.union(x["Suggests_Parsed"])


    childrens.add(x.name)

    if len(deps) == 0: # Touches the leaves

        return childrens

    # Adding itself in the list of childrens

    alreadySeen.add(x.name)

    for dep in deps:


        newX = ground_truth.loc[dep]

        childrensChildren = newX[mode+"_Childrens"]

        if len(childrensChildren) == 0:

            childrensChildren = recursiveOnly(newX, df, alreadySeen)



        childrens = childrens.union(childrensChildren)
        childrens.add(dep)
        alreadySeen.add(dep)

    return childrens


def compute_childrens(mode):
    ground_truth[mode+"_Summing"] = -1
    ground_truth[mode+"_Childrens"] = ""
    tot = len(ground_truth)

    for _, row in tqdm(ground_truth.iterrows(), total=tot):
        ground_truth.at[row.name, mode+"_Childrens"] = recursiveOnly(row, ground_truth, set(), mode)


def recursiveSearchOnDep(x, df, alreadySeen, mode="Depends"):

    """
    x : The current data Serie, Assuming that x contains Package, Version, Depends, Size and
        Summing dependances, Dependance traces for the dynamic approach

    summing : The sum of the size in Bytes
            df is the db we are performing the recursive search
    alreadySeen : Dict with the already seen packages + version
    mode :  `Depends` : include only Dependences
            `Recommends` : include Dependences, Recommandation
            `Suggests` : include Dependences, Recommandation and Suggests
    """

    childrens = set()

    if x.name in alreadySeen:
        return childrens



    deps = x["Depends_Parsed"]

    if mode == "Recommends":
        deps = deps.union(x["Recommends_Parsed"])

    if mode == "Suggests":
        deps = deps.union(x["Recommends_Parsed"])
        deps = deps.union(x["Suggests_Parsed"])


    childrens.add(x.name)

    if len(deps) == 0: # Touches the leaves

        return childrens

    # Adding itself in the list of childrens

    alreadySeen.add(x.name)

    for dep in deps:


        newX = df.loc[dep]


        childrensChildren = newX[mode + "_Childrens"]

        if len(childrensChildren) == 0:

            childrensChildren = recursiveSearchOnDep(newX, df, alreadySeen)



        #print("For ", dep, " we have childrens: ", childrensChildren)
        childrens = childrens.union(childrensChildren)
        childrens.add(dep)
        alreadySeen.add(dep)




    df.at[x.name, mode + "_Childrens"] = childrens


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

    return set(ids)

def compute_freq(ds):
    d = dict()
    all_childs = [x for y in ds.tolist() for x in y ]
    tot = len(all_childs)
    for child in tqdm(all_childs, total=tot) :

        if child not in d:
            d[child] = 1
        else:
            d[child] +=1

    s = pd.Series(d, name=m +'_Dependence_Frequency')
    return s

def generate_count_on_depend(ground_truth):

    ground_truth = ground_truth.fillna("")

    to_sort = []

    if "Depends" in ground_truth.columns:
        ground_truth["#Depends"] = ground_truth["Depends"].map(lambda x: 0 if x == "" else len(x.split(",")))
        to_sort += ["#Depends"]

    if "Recommends" in ground_truth.columns:
        ground_truth["#Recommends"] = ground_truth["Recommends"].map(lambda x: 0 if x == "" else len(x.split(",")))
        to_sort += ["#Recommends"]
    if "Suggests" in ground_truth.columns:
        ground_truth["#Suggests"] = ground_truth["Suggests"].map(lambda x: 0 if x == "" else len(x.split(",")))
        to_sort += ["#Suggests"]


    return ground_truth.sort_values(by = to_sort)


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
ground_truth = ground_truth.drop(axis= 1, columns=['Installed-Size', 'Maintainer', 'Description', 'parsedFrom', 'Homepage', 'Source', 'Section', 'Supported', 'Bugs', 'Origin' ,'capture_id','SHA1', 'Priority', 'Architecture', 'Description-md5', 'MD5sum', 'SHA256', 'packageMode' ])

gc.collect()

# Useful to sort the db and go a bit faster
ground_truth = generate_count_on_depend(ground_truth)


########### FOR TESTING #########
#ground_truth = ground_truth.sample(1500)
#################################


# Setting the dask DF
dground_truth = dd.from_pandas(ground_truth, npartitions=CORES)

#Used for Summing
dictSize = ground_truth["Size"].to_dict()



####################### MAIN ######################


for m in modes:

    # For each entry, we extract all the dependences and build the tree if required
    print("Parsing " +m)
    with ProgressBar():
        ground_truth[m+"_Parsed"] = dground_truth.map_partitions(lambda df: df[m].map((lambda row: parseAndFindDep(row, ground_truth)))).compute(scheduler = "multiprocessing")

    print("extracting childrens for "+m)

    # EXTRACT RELATION
    compute_childrens(m)

    ground_truth[m+"_Elements_involved"] = ground_truth[m+'_Childrens'].map(len)
    print("Elements involved per packages description: \n",ground_truth[m+"_Elements_involved"].describe())


    print("Summing : "+m)

    # Update the dask DF
    dground_truth = dd.from_pandas(ground_truth, npartitions=CORES)

    # For each entry we compute the high level of dependence
    with ProgressBar():
        ground_truth[m+"_Summing"] = dground_truth.map_partitions(lambda df: df[m+"_Childrens"].map((lambda x: computeSumOnDep(x, dictSize))), meta=('summingDep', int)).compute(scheduler = 'threads')

    print("Frequency of "+m)
    s = compute_freq(ground_truth[m+"_Childrens"])
    ss.append(s)

    ground_truth = ground_truth.drop(axis= 1, columns=[m])
    gc.collect()






# Add the Frequency series to the db
if "Depends" in modes:
    ground_truth = ground_truth.assign( Depends_Frequency= ss[0])

if "Recommends" in modes:
    ground_truth = ground_truth.assign( Recommends_Frequency= ss[1])

if "Suggests" in modes:
    ground_truth = ground_truth.assign( Suggests_Frequency= ss[2])


# Compute Freq in %
for m in modes:
    ground_truth[m+"_Freq_in_p"] = ground_truth[m+"_Frequency"].map(lambda x : x/len(ground_truth) )



print("Saving in csv: cleaned_and_expanded_gt.csv ")

to_drop = []
for m in modes:
    to_drop += ["#"+m]
    to_drop += [m+"_Parsed"]

ground_truth = ground_truth.drop(axis= 1, columns=to_drop)

ground_truth.to_csv("cleaned_and_expanded_gt.csv")

print("Done")
