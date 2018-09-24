# FingerPatch

This repository is part of my semester project "traffic-analysis on Software Updates". It is the continuation of the initial FingerPatch made by Ludovic Barman.

## Capture

Meant to interact with a Docker container, set up packet capture, pupeteer the container into fetching updates, record everything.

- `network.sh` to setup the IPTables
- `run.sh` for examples of how to manually command the docker image to update/do things
- `capture.py [TIMEOUT]` captures packets on NFQUEUE 0 for TIMEOUT duration / until Ctrl-C. Requires `sudo`
- `automate-capture.sh` automates the dowload of a packet+version

TODO: automate-capture.sh now logs everything to files, but we should store the data in a DB

## Crawl

More exhaustive approach, extract the `/etc/apt/source.list` to get the ground truth about available packages at what date. Fills in a database, allows to do basic queries.

## Graph-Fingerprintability-Repo

Simple analysis of whether packets are uniques or not (w.r.t size).

## Docs

Administrative documents, project report etc.
