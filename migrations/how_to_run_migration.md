Из корня:

pgmigrate migrate \
  -c "postgresql://postgres:postgres@localhost:5432/postgres" \
  -d . \
  -t latest