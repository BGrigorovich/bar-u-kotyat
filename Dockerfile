FROM python:3.9

RUN curl -sL "https://deb.nodesource.com/setup_16.x" | bash -
RUN apt update && \
    apt install -y nodejs && \
    apt clean

RUN npm install -g aws-cdk

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm awscliv2.zip

COPY . /code/
RUN pip install -r /code/requirements.txt

WORKDIR /code/
