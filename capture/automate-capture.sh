#!/bin/sh


UPDATE_TIMEOUT=100000
LOGDIR="logs"

if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi

# Clean the old fingerpatch countainer and iptables rules
# Create then the docker fingerpatch
sh clean_and_restart.sh

DOCKER_CONTAINER_ID=$(sudo docker ps --filter="name=fingerpatch" -q)

echo "run apt-get update on the docker (Ready to fetch the packages)"
sudo docker exec $DOCKER_CONTAINER_ID sh -c "apt-get update"

forwardingIsSetup=$(sudo iptables -L FORWARD --line-numbers -n | grep 172.100.0.100 -c)

# Set up IPtables to catch the updates
if [ "$forwardingIsSetup" -eq "0" ]; then
   echo "Setting up the forwarding rules in IPtables...";
   sudo iptables -I FORWARD -s 172.100.0.100 -j NFQUEUE --queue-num 0
    sudo iptables -I FORWARD -d 172.100.0.100 -j NFQUEUE --queue-num 0
else
    echo "Forwarding rules already set up in iptables"
fi

# This script assumes the docker image is running, ready to update, the traffic is piped to NFQUEUE 0

# test if alive
ALIVE=$(sudo docker exec $DOCKER_CONTAINER_ID sh -c "pwd")

if [ "$ALIVE" = "/" ]; then
    echo "Docker $DOCKER_CONTAINER_ID is alive, OK"
else
    echo "Docker $DOCKER_CONTAINER_ID cannot be contacted, aborting"
    exit 1
fi

# Set the package to update and the VERSION
PACKET=dpkg
VERSION=1.17.5ubuntu5.8

# extract infos from docker
TIMESTAMP=$(date +%s)
ARCHITECTURE=$(sudo docker exec $DOCKER_CONTAINER_ID sh -c "cat /etc/os-release | tr \"\\n\" \";\" ")
IDENTIFIER="${ARCHITECTURE}PACKET=$PACKET;PACKET_VERSION=$VERSION;TIMESTAMP=$TIMESTAMP"

OUTPUT=$(mktemp $LOGDIR/${TIMESTAMP}_XXXXX)
echo "Output is in $OUTPUT"
echo -n $IDENTIFIER > "$OUTPUT"
echo -en "\n\n" >> "$OUTPUT"



# start the interceptor
echo "Starting the capture, timeout in $UPDATE_TIMEOUT seconds..."
sudo python3 ./capture.py $UPDATE_TIMEOUT &

# echo "Starting the update, packet $PACKET version $VERSION"
echo "Executing sudo docker exec $DOCKER_CONTAINER_ID sh -c \"apt-get clean && apt-get install -d -y $PACKET=$VERSION\""
sudo docker exec $DOCKER_CONTAINER_ID sh -c "apt-get clean && apt-get install -d -y $PACKET=$VERSION"


echo "Closing interceptor"

kill -SIGTERM $!

#echo "Waiting for subprocesses..."
#wait
echo "Done"
