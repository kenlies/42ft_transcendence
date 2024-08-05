FROM python:3.11.4-slim-buster

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./websocket_matches .

EXPOSE 8001

RUN apt-get update && apt-get install -y netcat

COPY ./entry.sh .

RUN chmod +x entry.sh

CMD ["sh", "entry.sh"]
