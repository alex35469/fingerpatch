.PHONY: docker-start
docker-start:
	sudo systemctl start docker

.PHONY: docker-setup
docker-setup:
	./capture/network.sh

.PHONY: capture
capture:
	sudo python3 ./capture/capture.py

.PHONY: auto-capture
auto-capture:
	echo "Make sure you called apt-get update on the container before"
	(cd ./capture; ./automate-capture.sh)

.PHONY: extract-all
extract-all:
	echo "Make sure you called apt-get update and apt-get install zip on the container before"
	(cd ./capture; ./automate-capture.sh)

.PHONY: parse-into-mysql
parse-into-mysql:
	echo "Usage: python3 crawl/ubuntu-to-mysql.py crawl/apt_XXX/all_packages.txt"