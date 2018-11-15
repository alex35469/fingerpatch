#!/usr/bin/python3

import csv
import pymysql
import sys
import tqdm

with open("cleaned_and_expanded_gt.csv") as gt:
    gt_reader = csv.reader(gt)
    next(gt_reader, print)
    
    for entry in tqdm.tqdm(gt_reader):

    #ground_truth = pd.read_sql("SELECT * FROM `ubuntu_packets` ",connection)
        sql = "INSERT INTO `ubuntu_cleaned_packets` (`id`, `Package`, `Version`, `Size`, `Filename`, `Summing dependances`, `Elements involved`, `Childrens`, `Frequency`,`Freq in p` ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"




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
