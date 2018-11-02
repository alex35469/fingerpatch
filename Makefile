RANDOM=3

.PHONY: docker-setup
docker-setup:
	sh ./capture/clean_and_restart.sh


.PHONY: random-capture
random-capture:
	echo "Make sure you called 'make docker-setup' beforehand"
	(cd ./capture; python3 ./pickSome.py $(RANDOM); sh ./automate-capture.sh package.txt)


.PHONY: debug-docker
debug-docker:
	docker ps

.PHONY: deterministic-capture
deterministic-capture:
	echo "Make sure you called 'make docker-setup' beforehand"
	echo "Make sure you filled package.txt with the packages you want to simulate the capture"
	echo "With the appropriate syntax"

	(cd ./capture; sh ./automate-capture.sh package.txt)

.PHONY: match-capture
match-capture:
	(cd ./attack; python3 ./matching.py)



#.PHONY: extract-all
#extract-all:
#	echo "Make sure you called apt-get update and apt-get install zip on the container before"
#	(cd ./capture; ./automate-capture.sh)

#.PHONY: parse-into-mysql
#parse-into-mysql:
#	echo "Usage: python3 crawl/ubuntu-to-mysql.py crawl/apt_XXX/all_packages.txt"
