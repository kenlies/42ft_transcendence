python manage.py makemigrations
python manage.py migrate

exec "uvicorn" "flow.asgi:application" "--host" "0.0.0.0"