#!/usr/bin/python3
from netfilterqueue import NetfilterQueue
from scapy.all import *
import socket
import sys
import signal
import time
from threading import Thread

#
# CONSTANTS
#

nfQueueID         = 0
maxPacketsToStore = 10000

individualPacketPrint = False
recomposeTCPStreamWhenSomePacketsWereNotCaptured = True

#
# GLOBALS
#

nextFreeId = 0
allPackets = {}
dnsLookupTable = {'172.100.0.100': 'target'}

#
# FUNCTIONS
#

def iprint(*s):
  if individualPacketPrint:
    print(s)

def dnsQueryType(qtype):
  if qtype == 1:
    return "A"
  elif qtype == 28:
    return "AAAA"
  elif qtype == 33:
    return "SRV"
  return str(qtype)


def reverseDNS(ip):
  if str(ip) in dnsLookupTable:
    return [str(ip),dnsLookupTable[str(ip)]]
  else:
    try:
      name = socket.gethostbyaddr(ip)
      dnsLookupTable[str(ip)] = name[0]
      return [str(ip),str(name[0])]
    except:
      return [str(ip)]

def IPProtocol(p):
  if p==1:
    return "ICMP"
  if p==6:
    return "TCP"
  if p==17:
    return "UDP"
  if p==41:
    return "IPv6"
  if p==5:
    return "IP-in-IP"
  return p

def tcpFlags(flags):
  o = []
  if flags & 1 != 0:
    o.append("FIN")
  if flags & 2 != 0:
    o.append("SYN")
  if flags & 4 != 0:
    o.append("RST")
  if flags & 8 != 0:
    o.append("PSH")
  if flags & 16 != 0:
    o.append("ACK")
  if flags & 32 != 0:
    o.append("URG")
  return o

def httpParse(payload):
  parts = payload.split('\r\n')
  return parts

def packetHandle(p):
    global nextFreeId, allPackets

    packetOut = {}
    packetOut['id'] = nextFreeId
    nextFreeId += 1
    packetOut['nextpackets'] = []
    packetOut['src'] = reverseDNS(p["IP"].src)
    packetOut['dst'] = reverseDNS(p["IP"].dst)
    packetOut['protocol'] = IPProtocol(p["IP"].proto)
    packetOut['len'] =  p["IP"].len

    iprint("id", packetOut['id'])
    iprint("src", ' -> '.join(reverseDNS(p["IP"].src)))
    iprint("dst", ' -> '.join(reverseDNS(p["IP"].dst)))
    iprint("pro", IPProtocol(p["IP"].proto))
    iprint("len", p["IP"].len)

    if p.haslayer("DNS"):
      packetOut['dns'] = p["DNS"].qd.qname.decode('utf-8')
      packetOut['dns-type'] = "QUERY"
      if p["DNS"].nscount > 0:
        packetOut['dns-type'] = "ANS"
      packetOut['dns-v'] = dnsQueryType(p["DNS"].qd.qtype)
      iprint("dns", packetOut['dns'])
      iprint("dns-type", packetOut['dns-type'])
      iprint("dns-v", packetOut['dns-v'])

    if p.haslayer("TCP"):
      packetOut['tcp-port'] = p["TCP"].dport
      packetOut['tcp-seq'] = p["TCP"].seq
      packetOut['tcp-ack'] = p["TCP"].ack
      packetOut['tcp-win'] = p["TCP"].flags
      packetOut['tcp-flag'] = tcpFlags(p["TCP"].flags)

      iprint("tcp-port", p["TCP"].dport)
      iprint("tcp-seq ", p["TCP"].seq)
      iprint("tcp-ack ", p["TCP"].ack)
      iprint("tcp-win ", p["TCP"].window)
      iprint("tcp-flag", tcpFlags(p["TCP"].flags))

      payloadLength = 0
      if str(p["TCP"].payload) != "":
        payloadLength = len(p["TCP"].payload)
      packetOut['tcp-payload'] = payloadLength
      iprint("tcp-payload", payloadLength)

      nextSeqNumber = packetOut["tcp-seq"] + packetOut["tcp-payload"]
      if "FIN" in packetOut['tcp-flag'] or "SYN" in packetOut['tcp-flag']: # SYN and FIN flags increase the seq number by 1, even with 0 payload
        nextSeqNumber+=1
      packetOut['tcp-next-seqnum'] = nextSeqNumber
      iprint("tcp-next-seqnum", nextSeqNumber)

    if p.haslayer("Raw") and p["TCP"].dport == 80: # correspond to HTTP
      httpParts = httpParse(p["Raw"].load.decode('utf-8'))
      iprint("http", httpParts)

      packetOut['http'] = httpParts

    allPackets[packetOut['id']] = packetOut

    # reconstitute unidirectional flow
    if p.haslayer("TCP"):
      found = False
      thisID = packetOut['id'] - 1
      while not found and thisID > 0:
        oldPacket = allPackets[thisID]
        if 'tcp-next-seqnum' in oldPacket:
          if oldPacket["tcp-next-seqnum"] == p["TCP"].seq:
            iprint("Found matching old packet", thisID)
            allPackets[thisID]['nextpackets'].append(packetOut['id'])
            found = True
            break;
        thisID -= 1
      if not found and not "SYN" in packetOut["tcp-flag"]:
        print("Warning: this TCP packet does not have a parent")
        if recomposeTCPStreamWhenSomePacketsWereNotCaptured:
          nPacketsMissing = 1
          found = False
          thisID = packetOut['id'] - 1
          while not found and nPacketsMissing < len(allPackets):
            while not found and thisID > 0:
              oldPacket = allPackets[thisID]
              if 'tcp-next-seqnum' in oldPacket:
                if oldPacket["tcp-next-seqnum"] + (nPacketsMissing * oldPacket["tcp-payload"]) == p["TCP"].seq:
                  print("Found matching old packet (modulo",nPacketsMissing,"packet dropped) ", thisID)
                  allPackets[thisID]['nextpackets'].append(packetOut['id'])
                  found = True
                  break;
              thisID -= 1
            nPacketsMissing += 1


def recursiveprint(packet, level):
  global allPackets

  padding = '    ' * level
  print(padding, packet['src'])
  print(padding, packet['dst'])
  print(padding, packet['protocol'])
  print(padding, packet['len'])

  if level == 0:
    print(padding, getParamOfSequence(packet, 'len'))

  if 'dns' in packet:
    print(padding, packet['dns'])
  if 'tcp-payload' in packet:
    print(padding, packet['tcp-payload'])
  if 'http' in packet:
    print(padding, packet['http'])

  for packetID in packet['nextpackets']:
    recursiveprint(allPackets[packetID], level+1)

def sum(list):
  acc = 0
  for l in list:
    acc += l
  return acc

def markSequence(packet):
  toMark = [packet]

  while len(toMark) > 0:
    packet = toMark.pop()
    if 'used' not in packet or not packet['used']:
      packet['used'] = True
      for packetID in packet['nextpackets']:
        toMark.append(allPackets[packetID])

def getParamOfSequence(packet, param):
  global allPackets

  toAnalyze = [packet]
  res = []

  while len(toAnalyze) > 0:
    packet = toAnalyze.pop()
    if 'used-paramseq-'+param not in packet or not packet['used-paramseq-'+param]:
      if param in packet:
        res.append(packet[param])
        packet['used-paramseq-'+param] = True
    for packetID in packet['nextpackets']:
      toAnalyze.append(allPackets[packetID])
  return res

def printSequences(packet):
  global allPackets

  if 'used' in packet and packet['used']:
    return
  markSequence(packet)

  print("####################################")
  # print DNS requests on their own
  if 'dns' in packet:
    print(packet['src'], "->", packet['dst'])
    header = "DNS "+packet['dns-v']+" "+packet['dns-type']
    print(header, packet['dns'])
  else:
    print(packet['src'], "->", packet['dst'])
    http_seq = getParamOfSequence(packet, 'http')
    len_seq = getParamOfSequence(packet, 'len')
    payload_seq = getParamOfSequence(packet, 'tcp-payload')

    print("HTTP:", http_seq)
    print("Len:", len_seq)
    print("Total Len:", sum(len_seq))
    print("TCP Payloads:", payload_seq)
    print("Total Payloads:", sum(payload_seq))

def packetReceived(pkt):
  iprint("------------------------------------------------------------------------------------------")
  parsedPacket = IP(pkt.get_payload());
  packetHandle(parsedPacket)
  pkt.accept();

def cleanup(signal, frame):
  global nfqueue
  print('Listener killed.')
  for id, p in allPackets.items():
    printSequences(p)
  nfqueue.unbind()
  print("Ressources cleaned.")
  os._exit(0)

def bindAndListen():
  global nfqueue
  print("Binding to NFQUEUE", nfQueueID)
  nfqueue = NetfilterQueue()
  nfqueue.bind(nfQueueID, packetReceived, maxPacketsToStore)
  try:
    nfqueue.run()
  except KeyboardInterrupt:
    cleanup(0,0)

#
# MAIN
#


# if killed, clean ressources
signal.signal(signal.SIGTERM, cleanup)

# do we timeout ?
timeoutVal = -1
if len(sys.argv) == 2: # 1 is "capture.py"
  timeoutVal = float(sys.argv[1])
  print("Going to timeout in", timeoutVal, "seconds")

# Create the thread, wait on it, cleanup on Interrupt
t = Thread(target=bindAndListen)
t.start()

try:
  if timeoutVal < 0:
    t.join()
  else:
    t.join(timeoutVal)
except KeyboardInterrupt:
  cleanup(0,0)

print("Program done.")
os._exit(0)
