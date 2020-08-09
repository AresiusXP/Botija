FROM python:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
        python3-dev \
        unixodbc-dev

# Download SQL Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
        curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
        apt-get update && \
        echo msodbcsql17 msodbcsql/ACCEPT_EULA boolean true | debconf-set-selections && \
        apt-get install msodbcsql17 -y

# Create and copy files
RUN mkdir /app
RUN mkdir /app/images/
WORKDIR /app

COPY *.py /app/
COPY images/* /app/images/
COPY requirements.txt /app

# Installing pip dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["python3", "botija.py"]