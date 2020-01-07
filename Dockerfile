FROM python:3.7.0-alpine3.8

COPY ./create_service.py /usr/bin/create_service.py
COPY ./entrypoint.sh /usr/bin/entrypoint.sh

RUN pip install --upgrade pip
RUN pip3 install requests
RUN apk add --no-cache bash && chmod a+x /usr/bin/*

ENTRYPOINT [ "/usr/bin/create_service.py" ]