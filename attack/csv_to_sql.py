#!/usr/bin/python3

import csv
import pymysql
import sys
from tqdm import tqdm
import pandas as pd


def format_header(header):
    s = ''
    for h in header:
        s +="`"+h+"`,"
    return s[:-1]


with open("cleaned_and_expanded_gt.csv") as gt:
    gt_reader = csv.reader(gt)


    header = next(gt_reader)
    entries = format_header(header)
    valu = ((len(entries.split(",")))*"%s,")[:-1]
    print(valu)
    print(entries)
#    sys.exit(1)

    for entry in tqdm(gt_reader):

    #ground_truth = pd.read_sql("SELECT * FROM `ubuntu_packets` ",connection)
        sql = "INSERT INTO `ubuntu_cleaned_packets` (" +entries+ ") VALUES (" +valu+ ");"




        connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

        try :
            with connection.cursor() as cursor :
                cursor.execute(sql,entry)
                connection.commit()


        except Exception as e:
            print("Package id = {} couldn't be commited to the db due to: \n  {}".format(entry[0], e))


    connection.close()
