echo "deleting docker"
docker rm -f docker_con_463fb793-f179-4c65-a5b1-bf4f7b8037c0

echo "starting server"
python manage.py runserver