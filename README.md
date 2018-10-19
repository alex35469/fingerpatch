# FingerPatch

This repository is part of my semester project "traffic-analysis on Software Updates". It is the continuation of the initial FingerPatch made by Ludovic Barman.

## Capture

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


## Crawl

More exhaustive approach, extract the `/etc/apt/source.list` to get the ground truth about available packages at what date. Fills in a database, allows to do basic queries.


## Attack

Once the capture has been done and the ground truth has been established (in Crawl), the analysis of the two happens in the attack folder. Where the attacker succeed if he can with high probabilities match a captured package to a crawled package.


## Graph-Fingerprintability-Repo

Simple analysis of whether packets are uniques or not (w.r.t size).

## Docs

Administrative documents, project report etc.
