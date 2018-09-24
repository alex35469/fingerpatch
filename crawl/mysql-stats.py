#!/usr/bin/python3
from pathlib import Path
import sys
import pymysql.cursors
from math import *
import operator

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='fingerpatch',
                             password='fingerpatch',
                             db='fingerpatch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


packetStore = []

if len(sys.argv) != 2:
    print("Please supply a capture ID")
    sys.exit(1)

captureID=sys.argv[1]

def isascii(s):
    return len(s) == len(s.encode())
def tryFetch(array, key, default):
    if key in array and isascii(array[key]):
        return array[key]
    return default

data = [];

try:
    with connection.cursor() as cursor:# Create a new record
        sql = "SELECT `Package`,`Architecture`,`Version`,`Size` FROM `ubuntu_packets` WHERE `capture_id` = %s ORDER BY `Package` ASC"
        cursor.execute(sql, (captureID))
        data = cursor.fetchall()

finally:
    connection.close()

mapSizeToPackets = {}
    
f = open("sizes.out","w")
for line in data:
    size = line['Size']
    
    if not size in mapSizeToPackets:
        mapSizeToPackets[size] = []

    alreadyContainsIt = False
    for otherPacket in mapSizeToPackets[size]:
        if otherPacket['Package'] == line['Package'] and otherPacket['Architecture'] == line['Architecture'] and otherPacket['Version'] == line['Version'] and otherPacket['Size'] == line['Size']:
            alreadyContainsIt = True

    if not alreadyContainsIt:
        f.write(str(line['Size'])+"\n")
        mapSizeToPackets[size].append(line)

f.close()
histogram = {}
histogramValues = {}

for size in mapSizeToPackets:
    occurences = len(mapSizeToPackets[size])
    if not occurences in histogram:
        histogram[occurences] = 0;
        histogramValues[occurences] = [];
    histogram[occurences] += 1
    histogramValues[occurences].append(mapSizeToPackets[size])
print("Number of packages with unique sizes", histogram[1])

total = 0
for key in histogram:
    total += histogram[key]

for key in histogram:
    print("Number of packages with", key, "-unique sizes:", histogram[key], str(round(10000*histogram[key]/total)/100)+"%")

def padme(L):
    L = int(L)
    U = int(ceil(log(L))+1)
    V = int(ceil(log(U))+1)
    lastBits = U-V

    bitMask = (2 ** lastBits - 1)

    if L & bitMask == 0:
        return L

    L += (1 << lastBits)
    L = ((L >> lastBits) << lastBits)

    return L

print("---------------------------------")

padded = {}

for size in mapSizeToPackets:
    vals = mapSizeToPackets[size]
    B = padme(size)
    if not B in padded:
        padded[B] = []

    padded[B].extend(vals)

histogram = {}
histogramValues = {}

for size in padded:
    occurences = len(padded[size])
    if not occurences in histogram:
        histogram[occurences] = 0;
        histogramValues[occurences] = [];
    histogram[occurences] += 1
    histogramValues[occurences].append(padded[size])
print("Number of packages with unique sizes", histogram[1])

histogram = sorted(histogram.items(), key=operator.itemgetter(0))

total = 0
for key in histogram:
    uniqueness=key[0]
    numberOfPackets=key[1]
    total += numberOfPackets

for key in histogram:
    uniqueness=key[0]
    numberOfPackets=key[1]

    print("Number of packages with", uniqueness, "-unique sizes:", numberOfPackets, str(round(10000*numberOfPackets/total)/100)+"%")