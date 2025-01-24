BASE_DIR="/home/ayushkhaire/code/accessweb/accessweb"
DOCKER_FIELD="/home/ayushkhaire/code/accessweb/selenium_capture"

echo "deleting docker"
docker rm -f docker_con_463fb793-f179-4c65-a5b1-bf4f7b8037c0

cd ${BASE_DIR}/browse/chrome
echo "building again"
docker build --no-cache -t selenium_capture . 
echo "Complete build"
cd /${BASE_DIR}

echo "running server"
python manage.py runserver