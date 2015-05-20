FROM ubuntu:14.04

RUN apt-get update && \
    apt-get install -y \
        curl \
        git \
        python-pip \
        gunicorn

RUN mkdir /home/newsreader && \
    chown nobody /home/newsreader

USER nobody
ENV HOME=/home/newsreader
WORKDIR /home/newsreader

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000"]
EXPOSE 8000
CMD ["app:app"]

COPY ./requirements.txt /home/newsreader/app/
RUN pip install --user -r /home/newsreader/app/requirements.txt
COPY ./app /home/newsreader/app/

