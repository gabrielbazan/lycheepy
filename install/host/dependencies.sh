# Host Dependencies Installation Script

sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install -y openssh-server

# Docker CE installation
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce

# Docker compose installation
sudo apt-get install -y docker-compose

