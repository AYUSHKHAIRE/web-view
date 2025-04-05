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
mkdir ~/accessweb 
cd ~/accessweb
python3  -m venv env
source env/bin/activate

# clone the repository 
git clone https://github.com/AYUSHKHAIRE/web-view.git
cd web-view 

# install the requirements
pip install -r requirements.txt

sudo ufw allow 8000

# download model 
cd accessweb/browse/
mkdir assets
cd assets
gdown "https://drive.google.com/uc?id=13rZDduDh1LHnO7VC4_3qTnc183vlm0ow" -O asl_cnn_model.h5


# =======================================================================

# firewall 

gcloud compute firewall-rules list --filter="name~'http'"

gcloud compute firewall-rules create allow-django-8000 \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow Django on port 8000"

# =======================================================================

# build database and superuser 
cd ~/accessweb/web-view/accessweb/
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# add ip to ALLOWED_HOSTS in settings.py
sudo nano accessweb/settings.py
# make the admin , profile and test 

# run the server
python manage.py runserver 0.0.0.0:8000

# build the docker container
# after reboot , come back , do SSH again .
cd browse/chrome/
sudo touch credscloud.json
sudo nano credscloud.json
# paste the content of the credscloud.json file here
sudo touch .env 
sudo nano .env
# paste the content of the .env file here
# give docker permission wirthout sudo
sudo usermod -aG docker $USER 
sudo reboot 
cd accessweb/web-view/accessweb/browse/chrome/
docker build -t selenium_capture .

# ==========================================================

# if disk gets full
docker system prune -a -f
docker volume prune -f
sudo apt-get autoremove -y
sudo apt-get clean
sudo journalctl --vacuum-time=1d

# ==========================================================

source ~/accessweb/env/bin/activate
cd ~/accessweb/web-view/accessweb/
python manage.py runserver 0.0.0.0:8000

# ==========================================================

# dry gunicorn run 
gunicorn --bind 0.0.0.0:8000 accessweb.wsgi 
# will not render static files 

# ===========================================================
python manage.py collectstatic
pwd 
# /home/codeeayush/accessweb/web-view/accessweb

sudo nano /etc/systemd/system/gunicorn.socket
# paste the content of the gunicorn.socket file here
sudo nano /etc/systemd/system/gunicorn.service
# paste the content of the gunicorn.service file here
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
file /run/gunicorn.sock
sudo systemctl status gunicorn.socket 
sudo journalctl -u gunicorn.socket
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service
sudo systemctl status gunicorn.service
curl --unix-socket /run/gunicorn.sock
sudo systemctl status gunicorn.service
sudo nano /etc/nginx/sites-available/accessweb
sudo rm /etc/nginx/sites-enabled/accessweb
sudo ln -s /etc/nginx/sites-available/accessweb /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
# Give 'others' read on files and execute (cd) on folders
sudo chmod -R o+r /home/ayushkhaire/code/accessweb/accessweb/staticfiles/
sudo find /home/ayushkhaire/code/accessweb/accessweb/staticfiles/ -type d -exec chmod o+x {} \;
sudo nginx -t       # Check config
sudo systemctl reload nginx
sudo tail -n 30 /var/log/nginx/error.log 
sudo tail -n 30 /var/log/nginx/access.log 
sudo systemctl daemon-reexec
sudo systemctl restart gunicorn