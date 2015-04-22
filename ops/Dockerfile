FROM pypy:2

COPY . /code/
WORKDIR /code

CMD mkdir -p ./generated && ./generate.py
