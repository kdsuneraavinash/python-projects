FROM ubuntu:18.04

WORKDIR /app

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get -y install python3-pip
RUN pip3 install opencv-python
RUN apt-get install -y libsm6 libxext6
RUN apt-get install -y libxrender-dev
RUN pip3 install termcolor
RUN pip3 install progressbar2

ENV PYTHONIOENCODING=UTF-8

COPY . /app
CMD ["python3","serverhack.py"] 