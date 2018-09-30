#!/bin/sh

networkIsSetup=$(sudo docker network ls | grep fingerpatch -c)
containerStarted=$(sudo docker ps | grep fingerpatch -c)
forwardingIsSetup=$(sudo iptables -L FORWARD --line-numbers -n | grep 172.100.0.100 -c)


if [ "$networkIsSetup" -eq "0" ]; then
   echo "Creating the network fingerpatch...";
   sudo docker network create --subnet=172.100.0.0/16 fingerpatch
else
    echo "Network fingerpatch already set."
fi

if [ "$containerStarted" -eq "0" ]; then
   echo "Creating the container fingerpatch.";
   sudo docker run -d --name fingerpatch --net fingerpatch --security-opt seccomp:unconfined --ip 172.100.0.100 ubuntu:trusty-20180302 sleep 9999999
else
    echo "Container fingerpatch is already running."
fi

if [ "$forwardingIsSetup" -eq "0" ]; then
   echo "Setting up the forwarding rules in IPtables...";
   sudo iptables -I FORWARD -s 172.100.0.100 -j NFQUEUE --queue-num 0
    sudo iptables -I FORWARD -d 172.100.0.100 -j NFQUEUE --queue-num 0
else
    echo "Forwarding rules already set up in iptables."
fi
