#!/bin/sh

DOCKER_CONTAINER_STARTED=$(sudo docker ps | grep fingerpatch | wc -l)
if [ "$DOCKER_CONTAINER_STARTED" -eq "0" ]; then
    echo "Container not found, please run make docker-setup in parent folder."
    exit 1
fi

DOCKER_CONTAINER_ID=$(sudo docker ps --filter="name=fingerpatch" -q)

PACKET=dpkg
VERSION=1.17.5ubuntu5.8

UPDATE_TIMEOUT=5
LOGDIR="logs"

# This script assumes the docker image is running, ready to update, the traffic is piped to NFQUEUE 0

# test if alive
ALIVE=$(sudo docker exec $DOCKER_CONTAINER_ID sh -c "pwd")

if [ "$ALIVE" == "/" ]; then
    echo "Docker $DOCKER_CONTAINER_ID is alive, OK"
else
    echo "Docker $DOCKER_CONTAINER_ID cannot be contacted, aborting"
    exit 1
fi

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

echo "Waiting for subprocesses..."
wait
echo "Done"