#!/bin/bash

# Update package list
apt update 

# Install required dependencies
apt install -y ca-certificates curl gnupg lsb-release

# Setup Docker repository
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | tee /etc/apt/keyrings/docker.asc > /dev/null
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update and install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker service
systemctl start docker
systemctl enable docker

# Install Redis
apt install -y redis-server

# Start and enable Redis service
systemctl start redis-server
systemctl enable redis-server

# Print versions to verify installation
docker --version
redis-server --version
