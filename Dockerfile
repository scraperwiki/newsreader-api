FROM ubuntu:14.04

RUN apt-get update && \
    apt-get install -y \
        curl \
        git \
        python-pip \
        gunicorn

COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY ./app /app/

ENTRYPOINT ["gunicorn"]
CMD ["app:app"]
