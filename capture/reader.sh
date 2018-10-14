#!/bin/bash


while IFS='' read -r line || [[ -n "$line" ]]; do
    PACKAGE="$(echo $line | cut -d'_' -f1)"
    VERSION="$(echo $line | cut -d'_' -f2)"
    ARCHITECTURE="$(echo $line | cut -d'_' -f3)"
    SIZE="$(echo $line | cut -d'_' -f4)"
    echo "Packet = $PACKAGE    |       Version = $VERSION"
done < "$1"
