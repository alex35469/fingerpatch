RANDOM=3
NB_DEPENDS=-1


.PHONY: extract-packages
extract-packages:
	$(info Make sure you run make docker-setup before)
	(cd ./crawl/;sh extract-ubuntu.sh)

.PHONY: crawled_package-to-mysql
crawled_package-to-mysql:
	$(info Usage: python3 crawl/ubuntu-to-mysql.py crawl/apt_XXXX/all_packages.txt)
	$(info where XXXX is the directory generated by the desired crawl so the following:)
	@ ls -l crawl | grep apt_

.PHONY: cleaned_package-to-mysql
cleaned_package-to-mysql:
	(cd ./attack/; python3 csv_to_sql.py )


.PHONY: clean_crawl
clean_crawl:
	(cd ./attack/; python3 clean_substract_gt.py)

.PHONY: docker-setup
docker-setup:
	sh ./capture/clean_and_restart.sh

.PHONY: docker-debug
docker-debug:
	PID=$(ps ax | grep "python3 ./capture" | head -1  | awk '{print $1;}')
	sudo kill $PID

.PHONY: random-capture
random-capture:
	$(info Make sure you called 'make docker-setup' beforehand)
	(cd ./capture; python3 ./pickSome.py $(RANDOM) $(NB_DEPENDS); sh ./automate-capture.sh package.txt)

.PHONY: kernel-update-capture
kernel-capture:
	$(info Make a capture from kernel x to kernel y where x is the first line of kernel.txt and y is the second line)
	(cd ./capture; sh ./automate-capture.sh kernel-update.txt true)

.PHONY: deterministic-capture
deterministic-capture:
	$(info Make sure you called 'make docker-setup' beforehand)
	$(info Make sure you filled package.txt with the packages you want to simulate the capture with the appropriate syntax)

	(cd ./capture; sh ./automate-capture.sh package.txt)

.PHONY: match-match-capture-usingOldCaptures
match-capture-usingOldCaptures:
	(cd ./attack; python3 ./matching.py	useOldCapture)

.PHONY: match-capture
match-capture:
	(cd ./attack; python3 ./matching.py)
