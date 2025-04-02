#!/bin/bash

# https://www.codewithharry.com/blogpost/django-deploy-nginx-gunicorn/

# Update package list
sudo apt update 

# Install required dependencies
sudo apt install -y ca-certificates curl gnupg lsb-release

# Setup Docker repository
sudo mkdir -p /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# install docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Redis
sudo apt install -y redis-server

# install nginx
sudo apt install -y nginx 

# install git 
sudo apt install -y git

# install python3
sudo apt install -y python3 python3-pip python3-venv

# package library for opencv
sudo apt update
sudo apt install -y libgl1

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl status docker

# Start and enable Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server

# Print versions to verify installation
docker --version
redis-server --version
python3 --version
nginx -v
git --version

# make a virtual environment
sudo pip3 install virtualenv
mkdir ~/accessweb 
cd ~/accessweb
virtualenv env
source env/bin/activate

# clone the repository 
git clone https://github.com/AYUSHKHAIRE/web-view.git
cd web-view 

# install the requirements
pip install -r requirements.txt

sudo ufw allow 8000

# download model 
gdown "https://drive.google.com/uc?id=13rZDduDh1LHnO7VC4_3qTnc183vlm0ow" -O /home/codeeayush/accessweb/web-view/accessweb/browse/assets/asl_cnn_model.h5
