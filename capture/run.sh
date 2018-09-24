#!/bin/sh

# search for a package
# apt-cache madison package name
# or
# apt-get install devscripts, and
# rmadison package name

# download a package (and its dep)
# apt-get clean && apt-get -d -y package=version
# apt-get clean && apt-get install -d -y wireguard-dkms=0.0.20170214-1
# apt-get clean && apt-get install -d -y -s libkmod2=22-1.1ubuntu1