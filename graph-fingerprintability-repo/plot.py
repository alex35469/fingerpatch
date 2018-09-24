#!/bin/python3

# plot with python padding-size-vs-L.py | gnuplot -p -e "plot '<cat'"

from math import *
import sys
import matplotlib.pyplot as plt

data = {}
with open('data') as f:
    for ln in f:
        d = ln.split(',')
        key = int(d[0])
        val = float(d[2])
        data[key]=val

data_padded = {}
with open('data_padded') as f:
   for ln in f:
        d = ln.split(',')
        key = int(d[0])
        val = float(d[2])
        data_padded[key]=val

#plot data

plt.plot(data.keys(), data.values(), label='Non-padded')
plt.plot(data_padded.keys(), data_padded.values(), label='Padded')
plt.legend(loc='upper left')

#plt.xscale('log')
#plt.yscale('log')

plt.xlim([0,10])

plt.xlabel('Packet uniqueness')
plt.ylabel('Packet count')

#show plot
plt.show()
