 #!/bin/sh

# Supposing we are downloading at 100KB/s
DOWNLOAD_RATE=100000
SAFETY_MARGIN=6

LOGDIR="logs"
NAME="all_captures"


if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi


DOCKER_CONTAINER_ID=$(sudo docker ps --filter="name=fingerpatch" -q)

containerStarted=$(sudo docker ps -a| grep fingerpatch -c)
if [ "$containerStarted" -ne "1" ]; then
  echo "Please make sur you prepared the docker to the capture (sh clean_andprepare.sh)"
fi


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



# extract infos from docker
#TIMESTAMP=$(date +%s)
#ARCHITECTURE=$(sudo docker exec $DOCKER_CONTAINER_ID sh -c "cat /etc/os-release | tr \"\\n\" \";\" ")
#IDENTIFIER="${ARCHITECTURE}PACKET=$PACKET;PACKET_VERSION=$VERSION;TIMESTAMP=$TIMESTAMP"

OUTPUT="$LOGDIR/$NAME"
if [ ! -d "$OUTPUT" ]; then
  touch $OUTPUT
fi
echo "Output is in $OUTPUT"
echo -n $IDENTIFIER > "$OUTPUT"
echo -en "\n\n" >> "$OUTPUT"

# Set the package to update and the VERSION
#PACKET=weechat-doc
#VERSION=0.4.2-3ubuntu0.1

# Loop on the packet name, version, architecture and size
while IFS='' read -r line ; do
  ID="$(echo $line | cut -d',' -f1)"
  PACKAGE="$(echo $line | cut -d',' -f2)"
  VERSION="$(echo $line | cut -d',' -f3)"
  SIZE="$(echo $line | cut -d',' -f4)"


  UPDATE_TIMEOUT=$(python3 -c "from math import ceil; print(ceil($SIZE/$DOWNLOAD_RATE)+$SAFETY_MARGIN)")

  echo "################## Capture $PACKAGE=$VERSION expected: $SIZE bits, ID $ID ###########################"
  # start the interceptor
  echo "Starting the capture, timeout in $UPDATE_TIMEOUT seconds..."

  sudo python3 ./capture.py $UPDATE_TIMEOUT $ID & #>> $OUTPUT &
  PID=$!
  # echo "Starting the update, packet $PACKET version $VERSION"
  # Can see list of upgradable package with apt list --upgradable
  echo "Executing sudo docker exec $DOCKER_CONTAINER_ID sh -c \"apt-get clean && apt-get install -d -y $PACKAGE=$VERSION\""
  sudo docker exec $DOCKER_CONTAINER_ID sh -c "apt-get clean && apt-get install -d -y $PACKAGE=$VERSION"



  # Fetch the PID of capture process
  #PID=$(ps ax | grep "python3 ./capture" | head -1  | awk '{print $1;}')

  echo "--Waiting for pid=$PID (Time out was $UPDATE_TIMEOUT (sudo kill $PID to save time)--"

  # Have to find out how to Send a SIGTERM to children process 
  #sudo kill -10 $PID


  wait $PID

  echo "Done"
done < "$1"
