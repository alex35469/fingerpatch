
containerStarted=$(sudo docker ps -a| grep fingerpatch -c)
forwardingIsSetup=$(sudo iptables -L FORWARD --line-numbers -n | grep 172.100.0.100 -c)
networkIsSetup=$(sudo docker network ls | grep fingerpatch | wc -l)


if [ "$containerStarted" -eq "1" ]; then
  echo "stop fingerpatch docker"
  sudo docker stop fingerpatch
  echo "Remove old docker fingerpatch"
  sudo docker rm fingerpatch
fi

if [ "$forwardingIsSetup" -eq "2" ]; then
   echo "Delete old forwarding rules in IPtables...";
   sudo iptables -D FORWARD -s 172.100.0.100 -j NFQUEUE --queue-num 0
   sudo iptables -D FORWARD -d 172.100.0.100 -j NFQUEUE --queue-num 0
fi

if [ "$networkIsSetup" -eq "0" ]; then
   echo "Creating the network fingerpatch...";
   sudo docker network create --subnet=172.100.0.0/16 fingerpatch
else
    echo "Network fingerpatch already set."
fi


echo "setting new docker fingerpatch"
#sudo docker run -d --name fingerpatch --net fingerpatch --ip 172.100.0.100 ubuntu:trusty-20150427 sleep 9999999
sudo docker run -d --name fingerpatch --net fingerpatch --security-opt seccomp:unconfined --ip 172.100.0.100 ubuntu:trusty-20180302 sleep 9999999

echo "run apt-get update on the docker (Ready to fetch the packages)"
sudo docker exec fingerpatch sh -c "apt-get update"
