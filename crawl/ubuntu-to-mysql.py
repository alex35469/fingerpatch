#!/usr/bin/python3
from pathlib import Path
import sys
import pymysql.cursors
import json
from tqdm import tqdm

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


packetStore = []

if len(sys.argv) != 2:
    print("Please supply a filepath for all_package.txt")
    sys.exit(1)

fileName=sys.argv[1]
rawText = Path(fileName).read_text()
rawText = '['+rawText.strip()+']'
rawText = rawText.replace(',]', ']')
packets = json.loads(rawText)

def isascii(s):
    return len(s) == len(s.encode())
def tryFetch(array, key, default):
    if key in array and isascii(array[key]):
        return array[key]
    return default

try:
    with connection.cursor() as cursor:# Create a new record
        sql = "INSERT INTO `ubuntu_ready` (`done`) VALUES (%s)"
        cursor.execute(sql, (False))

        connection.commit();

        sql = "SELECT `id` FROM `ubuntu_ready` ORDER BY `id` DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        captureID = result['id']



        # Create a new record
        for packet in tqdm(packets, total = len(packets)):

            sql = "INSERT INTO `ubuntu_packets` (`capture_id`,`Priority`,`Version`,`Maintainer`,`SHA1`,`Description`,`Installed-Size`,`parsedFrom`,`Description-md5`,`Package`,`Architecture`,`Bugs`,`Origin`,`MD5sum`,`Depends`,`Recommends`, `Suggests`,`Homepage`,`Size`,`Source`,`SHA256`,`Section`,`Supported`,`Filename`,`packageMode`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = (captureID, tryFetch(packet,'Priority', ''), tryFetch(packet,'Version', ''), tryFetch(packet,'Maintainer', ''), tryFetch(packet,'SHA1', ''), tryFetch(packet,'Description', ''), tryFetch(packet,'Installed-Size', -1), tryFetch(packet,'parsedFrom', ''), tryFetch(packet,'Description-md5', ''), tryFetch(packet,'Package', ''), tryFetch(packet,'Architecture', ''), tryFetch(packet,'Bugs', ''), tryFetch(packet,'Origin', ''), tryFetch(packet,'MD5sum', ''), tryFetch(packet,'Depends', ''), tryFetch(packet, 'Recommends', ''), tryFetch(packet, 'Suggests', ''), tryFetch(packet,'Homepage', ''), tryFetch(packet,'Size',-1), tryFetch(packet,'Source', ''), tryFetch(packet,'SHA256', ''), tryFetch(packet,'Section', ''), tryFetch(packet,'Supported', ''), tryFetch(packet,'Filename', ''), tryFetch(packet,'packageMode', ''))
            cursor.execute(sql, data)
        connection.commit();


        sql = "UPDATE `ubuntu_ready` SET `done`=%s WHERE `id`=%s"
        cursor.execute(sql, (True, captureID))
        connection.commit();

finally:
    connection.close()
