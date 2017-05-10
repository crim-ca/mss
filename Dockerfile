FROM python:2.7-alpine
MAINTAINER frederic.osterrath@crim.ca

RUN apk update &&\
    apk add build-base\
            linux-headers\
            bash &&\
    pip install pbr==1.8.0\
                python-keystoneclient==1.7.1\
                python-swiftclient==2.6.0\
                gunicorn==19.3.0 &&\
    pip install mercurial==3.4 &&\
    apk del build-base\
            linux-headers

# Thanks to a bug in pbr, this is the only way to expose its version to swift.
ENV PBR_VERSION 1.8.0

# App
COPY . /usr/local/src/mss
RUN pip install /usr/local/src/mss gunicorn

RUN mkdir -p /data
RUN mkdir -p /opt/mss

COPY deployment/conf.py /opt/mss/config.py
COPY logging.conf /opt/mss/logging.conf

ENV VRP_CONFIGURATION /opt/mss/config.py

EXPOSE 5000

WORKDIR /opt/mss

RUN python -m mss.init_swift_container

CMD ["gunicorn", "-w", "4", "-preload", "-b", "0.0.0.0:5000", "mss.rest_api:APP", "--log-config=logging.conf"]
