if [ "$DATABASE" = "postgres" ]
then
    echo "Wait PostgreSQL startup"

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL ready"
fi

python manage.py makemigrations
python manage.py migrate

exec "uvicorn" "flow.asgi:application" "--host" "0.0.0.0"