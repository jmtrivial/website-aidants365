docker-compose down -v --remove-orphans
docker-compose -f docker-compose.yml up -d --build
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput
cat cbackup-2022-03-14.json | docker-compose -f docker-compose.yml  exec -T web python manage.py loaddata --format=json -
