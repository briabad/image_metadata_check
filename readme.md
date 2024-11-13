
sudo apt update
sudo apt-get update
sudo apt upgrade -y
sudo apt install git curl unzip tar make sudo vim wget -y
sudo apt install python3-pip
pip3 install -r requirements.txt



sudo apt-get update -y
sudo apt-get upgrade

#Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

Es necesaria crear una ec2 exponiendo la direccion ip a internet, es neceario habilitar en la seccion de seguridad en "Inbound rules"