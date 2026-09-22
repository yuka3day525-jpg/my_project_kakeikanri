
#!/usr/bin/env bash
set -e

cp demo_seed.sqlite3 db_demo.sqlite3

python manage.py collectstatic --noinput

exec gunicorn myproject.wsgi:application