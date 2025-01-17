FROM python:3.10

WORKDIR /session

COPY . /session

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

CMD [ "python", "script.py" ]