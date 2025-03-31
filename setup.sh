#!/bin/bash

# Update package list
sudo apt update 

# Install required dependencies
sudo apt install -y ca-certificates curl gnupg lsb-release

# Setup Docker repository
sudo mkdir -p /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
chmod a+r /etc/apt/keyrings/docker.asc
sudo echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# install docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl status docker

# Install Redis
sudo apt install -y redis-server

# Start and enable Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server

# Print versions to verify installation
docker --version
redis-server --version

# install python3
sudo apt install -y python3 python3-pip python3-venv