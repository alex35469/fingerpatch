#!/bin/sh

echo "Please run \"make capture\" in the main folder so the container has internet access"

DOCKER_CONTAINER_STARTED=$(sudo docker ps | grep fingerpatch | wc -l)
if [ "$DOCKER_CONTAINER_STARTED" -eq "0" ]; then
    echo "Container not found, please run make docker-setup in parent folder."
    exit 1
fi

DOCKER_CONTAINER_ID=$(sudo docker ps --filter="name=fingerpatch" -q)

# compile available packets and fetch
sudo docker exec -it $DOCKER_CONTAINER_ID sh -c "apt-get update; cd /var/lib/apt/lists/; for d in *.gz; do gunzip \$d; done; rm -f *.gz; zip data.zip *; ls"
rm -f data.zip
sudo docker cp $DOCKER_CONTAINER_ID:/var/lib/apt/lists/data.zip .

# unzip and clean
OUTPUT=$(mktemp -d apt_XXXX )
mv data.zip $OUTPUT
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
