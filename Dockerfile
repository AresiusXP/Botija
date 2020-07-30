FROM python:latest

# Install dependencies
RUN apt update && apt install \
        python3 \
        python3-pip

# Installing pip dependencies
RUN pip3 install \
    signal \
    discord.py \
    dateutil

RUN mkdir /app
WORKDIR /app

COPY botija.py /app/botija.py
COPY sql.py /app/sql.py

CMD ["python3", "botija.py"]