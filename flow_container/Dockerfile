FROM python:3.11.4-slim-buster

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./flow .

EXPOSE 8000

COPY ./entry.sh .

RUN chmod +x entry.sh

CMD ["sh", "entry.sh"]
