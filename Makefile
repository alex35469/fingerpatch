RANDOM=3
NB_DEPENDS=-1


.PHONY: extract-packages
extract-packages:
	echo "Make sure you run make docker-setup before"
	(cd ./crawl/;sh extract-ubuntu.sh)

.PHONY: crawled_package-to-mysql
crawled_package-to-mysql:
	echo "Usage: python3 crawl/ubuntu-to-mysql.py cleaned_and_expanded_gt.csv"

.PHONY: cleaned_package-to-mysql
cleaned_package-to-mysql:
	(cd ./attack/; python3 csv_to_sql.py )


.PHONY: clean_crawl
clean_crawl:
	(cd ./attack/; python3 clean_substract_gt.py)

.PHONY: docker-setup
docker-setup:
	sh ./capture/clean_and_restart.sh

.PHONY: random-capture
random-capture:
	echo "Make sure you called 'make docker-setup' beforehand"
	(cd ./capture; python3 ./pickSome.py $(RANDOM) $(NB_DEPENDS); sh ./automate-capture.sh package.txt)


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
