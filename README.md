# FingerPatch

This repository is part of my semester project "traffic-analysis on Software Updates". It is the continuation of the initial FingerPatch made by Ludovic Barman. The goal of this project is to guess which package a victim is downloading. To have a quick overview of this project, please access the slides available here

## Requirements

Here are the following requirements in order to use fingerpatch:

- System requirements : `Linux` (for IPTables and NfQueue), enough memory and CPU to process data quickly.
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

      3. `make state-capture`. Download all the packages specfiy in xxx while making .

  8. final step. 2 mode of matching:

      1. `make stateless-matching`: Guessing which capture correspond to which package using using HTTP request matching and Size matching. Output directly the result in stdout and record it in fingerpatch's database.

      2. `make stateful-matching`:  Same as above except that we consider that some packages are already installed (this include also the default packages include in almost every machine. i.e. libc6)



  Once all the steps are done, you should find in `fingerpatch` 4 tables :

  - `ubuntu_packets` : Rawly crawled packages.
  - `ubuntu_captures` : Cleaned and extended version of the above.
  - `attack_table` : Where the attacker.
  - `ubuntu_ready` : helper table used for crawling.


## Repository structure
In this section, we give a complete explanation about the various directory and the files from which they are composed.


### Crawl

More exhaustive approach, extract the `/etc/apt/source.list` to get the ground truth about available packages at what date. Fills in a database, allows to do basic queries.


### Capture

Meant to interact with a Docker container, set up packet capture, pupeteer the container into fetching updates, record everything.

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

Once the capture has been done and the ground truth has been established (in Crawl), the analysis of the two happens in the attack folder. Where the attacker succeed if he can with high probabilities match a captured package to a crawled package.



## Issues


## Docs

Administrative documents, project report etc.
