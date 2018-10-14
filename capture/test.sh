#!/usr/bin/env bash

DR=60000
SAFETY_MARGIN=5
SIZE=1284462

TO=$(python3 -c "from math import ceil; print(ceil($SIZE/$DR)+$SAFETY_MARGIN) ")

echo $TO

#set -eux
#sudo sleep 30 &
#spid=$!
#sleep 1
#sudo kill -15 $spid
#wait $!
