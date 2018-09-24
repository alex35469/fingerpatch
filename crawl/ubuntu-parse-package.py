#!/usr/bin/python3
from pathlib import Path
import sys
import json

packetStore = []

if len(sys.argv) != 3:
    print("Please supply a filename + mode")
    sys.exit(1)

fileName=sys.argv[1]
packageMode=sys.argv[2] #release or source
#print("Gonna read", fileName, "in mode", packageMode)

def handlePacketDescription(desc):
    global packetStore, fileName, packageMode

    lines = desc.split('\n')
    packet = {}
    for l in lines:
        tmp = l.split(' ')
        key = tmp[0].replace(':', '')
        val = ' '.join(tmp[1:])
        packet[key] = val

    if len(packet) > 1:
        packet["parsedFrom"] = fileName
        packet["packageMode"] = packageMode
        packetStore.append(packet)

rawText = Path(fileName).read_text()

#split by \n\n
splitByPackets = rawText.split("\n\n")

for p in splitByPackets:
    handlePacketDescription(p)

# print all packets, comma separated
for p in packetStore:
    print(json.dumps(p, separators=(',',':')) + ",")