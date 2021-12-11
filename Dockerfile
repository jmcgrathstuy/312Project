FROM python:3.8.8

RUN apt-get update
RUN pip3 install pymongo
RUN pip3 install bcrypt

ENV Home /root
WORKDIR /root

COPY . .

EXPOSE 8000

CMD python server.py
