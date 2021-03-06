#!/bin/bash



echo "Please run \"make capture\" in the main folder so the container has internet access"

DOCKER_CONTAINER_STARTED=$(sudo docker ps | grep fingerpatch | wc -l)
if [ "$DOCKER_CONTAINER_STARTED" -eq "0" ]; then
    echo "Container not found, please run make docker-setup in parent folder."
    exit 1
fi

DOCKER_CONTAINER_ID=$(sudo docker ps --filter="name=fingerpatch" -q)

# Extending source.lists
echo $#
if [ "$#" -eq "1" ]; then
  sudo docker cp $1 $DOCKER_CONTAINER_ID:/etc/apt/sources.list
  #sudo docker exec -it $DOCKER_CONTAINER_ID sh -c "'echo  $EXTEND'  > /etc/apt/sources.list"
fi

# Get the list default packages
sudo docker exec fingerpatch sh -c "apt list --installed > default_packages.txt"

# compile available packets and fetch
sudo docker exec -it $DOCKER_CONTAINER_ID sh -c "apt-get update; apt-get install --no-install-recommends -y zip; cd /var/lib/apt/lists/; for d in *.gz; do gunzip \$d; done; rm -f *.gz; zip data.zip *; ls"

# removing ziè
sudo docker exec -it $DOCKER_CONTAINER_ID sh -c "apt-get remove -y zip; apt-get clean"

rm -f data.zip

# exporting from docker to the host machine
sudo docker cp $DOCKER_CONTAINER_ID:/default_packages.txt .
sudo docker cp $DOCKER_CONTAINER_ID:/var/lib/apt/lists/data.zip .

# unzip and clean
OUTPUT=$(mktemp -d apt_XXXX )
mv data.zip $OUTPUT
mv default_packages.txt $OUTPUT

cd $OUTPUT
unzip data.zip
rm -rf data.zip
rm -rf lock
rm -rf partial

# order
mkdir releases
mkdir sources
mkdir packages

for f in *_InRelease; do mv "$f" releases/; done
for f in *_Sources; do mv "$f" sources/; done
for f in *_Packages; do mv "$f" packages/; done

# extract all available packages
touch all_packages.txt

for f in packages/*
do
    python3 ../ubuntu-parse-package.py "$f" "releases" >> all_packages.txt
done
for f in packages/*
do
    python3 ../ubuntu-parse-package.py "$f" "source" >> all_packages.txt
done
