FROM python:3.8.8

ENV Home /root
WORKDIR /root

COPY . .

EXPOSE 8000

CMD python server.py
