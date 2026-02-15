docker-compose up -d

psql -U $(whoami) -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"

cd migrations
pgmigrate migrate -c migrations.yml -t latest

Для запуска докера из корня:
pgmigrate migrate \
  -c "postgresql://postgres:postgres@localhost:5432/postgres" \
  -d . \
  -t latest