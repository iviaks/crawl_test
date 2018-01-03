FROM python:3.5

ADD ./requirements.txt /tmp/r.txt
RUN pip install -r /tmp/r.txt
