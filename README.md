# FingerPatch

This repository is part of my semester project "traffic-analysis on Software Updates". It is the continuation of the initial FingerPatch made by Ludovic Barman. The goal of this project is to guess which package a victim is downloading. To have a quick overview of this project, please access the slides available [here](https://docs.google.com/presentation/d/1oDi0Ds2l3TXghT6AvLKKgyhFA--uFD9d9vGC6eFooss/edit#slide=id.p)

## Requirements

Here are the following requirements in order to use fingerpatch:

- System requirements : `Linux` (for IPTables and NfQueue), internet access, enough memory and CPU to process data quickly.
- database : `MySQL` db running on your System
- Python library : `pandas`, `pymysql`, `netfilterqueue`, `scapy`, `dask`. (All downloadable with pip.)
- Docker (to emulate the victim. the attacker is the host)


## Getting started
In the following, we show you the basic command to make a capture and guessing the update. Please refer to the next section for explanations.

  1. Import the skeleton of the database `fingerpatch` in MySQL. The structure of the fingerpatch database can be found at /utils/fingerpatch.sql. All the scripts will access the database by using a fingerpatch as the username and the password.

  2. `make docker-setup`. Create the victim through Docker

  3. `make extract-packages`. Extract the data that will be part of the attacker database in a folder named `apt_XXXX`

  4. `crawled_package-to-mysql`. Show the instruction to move the extracted data to the fingerpatch database. Follow them and fill the fingerpatch db.

  5. `make clean_crawl`. Generate cleaned_and_expanded_gt.csv, a cleaned and expanded version of the data that were generated in 3.

  6. `make cleaned_package-to-mysql`. Fill the fingerpatch db

  7. For this step, there are multiple options:

      1. `make deterministic-capture`. Make the victim download packages specify in /capture/package.txt while the attacker is recording it. Also fill the table `attack_table` with the data collected by the attacker.

      2. `make random-capture NB_DEPENDS=X RANDOM=Y`. Make Y random capture with packages only having NB_DEPENDS dependences. If no specify, RANDOM = 3 and NB_DEPENDS is taken randomly

      3. `make state-capture`. Download package x and then download and capture a package y. This is to emulate a victim how is doing a kernel update from x to y.

  8. final step. 2 mode of matching:

      1. `make stateless-matching`: Guessing which capture corresponds to which package using HTTP request matching and Size matching. Output directly the result in stdout and record it in fingerpatch's database.

      2. `make stateful-matching`:  Same as above except that we consider that some packages are already installed (this include also the default packages in almost every machine. i.e. libc6)



  Once all the steps are done, you should find in `fingerpatch` 4 tables :

  - `ubuntu_packets` : Rawly crawled packages.
  - `ubuntu_captures` : Cleaned and extended version of the above.
  - `attack_table` : Where the attacker.
  - `ubuntu_ready` : helper table used for crawling.


## Repository structure
In this section, we give a complete explanation about the various directory and the files from which they are composed.


### Crawl

The very first step that the attacker has to make is getting the database where he will be able to match captured package to  

on Ubuntu, (Linux dist.) the metadata of the apt packages are available in `/var/lib/apt/lists/`. To get this directory up-to-date, the attacker can run `apt-get update` before crawling it. This will fetch the latest packages' metadata by contacting the appropiate servers in `ect/apt/source.list`.

However, there are some packages' metadata not available by default. The attacker can add them by running `add-apt-repositories <repo-name>`. This is by exemple the case for the kernel packages which is not available by default. An attacker can still include them for crawling by running the above command with `ppa:teejee2008/ppa` as the repo name

After having crawled the metadata, the attacker is supposed to have in his database the whole crawled packages with full features as well as the a unique identifier `capture_id` which will be used to match a capture to a unique package. (in our case `ground_truth`)

contains :

TODO


### Capture

Meant to interact with a Docker container, set up packet capture, pupeteer the container into fetching updates, record everything.

TODO  : Finish description


contains the following files:

- `network.sh` to setup the IPTables
- `run.sh` for examples of how to manually command the docker image to update/do things
- `capture.py [TIMEOUT] [TRUTH_ID](opt.)` captures packets on NFQUEUE 0 for TIMEOUT duration / until Ctrl-C. Requires `sudo` it fills in the DB fingerpatch with the corresponding ID of the ground_truth once a TIMEOUT or Ctrl-C occurs.
- `automate-capture.sh [FILENAME]` automates the set-up of the docker, fetching updates, record the installation of the package using the file given as argument. Each line in the file represents a package to capture and is given by `truth_id,package,version,size`.
Where `truth_id` : Id of the associated package to download
      `package` : name of the package to download
      `version` : version of the package
      `size` : size of the package to download

`83973,x11proto-dmx-dev,1:2.3.1-2,5848` would be a correct entry.

 (TOFIX: Timeout doesn't really timeout need to manually kill the capture with `sudo kill PID`)





### Attack

The analysis of the ground_truth, the captures happens in the attack folder as well as trying to match the capture to the ground_truth.

The attack folder can be divided into 3 parts: __Cleaning__, __Mining__ and __Matching__









#### Cleaning
In the previous step, the attacker ends up with a raw database of the crawled Packages metadata. Many attributes of package's metadata are useless for the attacker. And might want to get rid of them. (i.e. the attacker may not want to keep the `Maintainer` field).

While doing a capture, the attacker will mostly only be interessted about the package's name and version the victim is updating. It make sense to drop every package's metadata that have the same size, name version and maybe architecture. This opperation will reduce his database and thus the time it will take to do a mapping  

#### Mining

After cleaning, the attacker still have some task to do before recording the Captures. Indeed,

#### Matching

Where the attacker succeed if he can with high probabilities match a captured package to a crawled package.


## Issues


## Docs

Administrative documents, project report etc.
