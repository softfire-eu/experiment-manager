FROM python:3.5
# File Author / Maintainer
MAINTAINER SoftFIRE


RUN mkdir -p /var/log/softfire && mkdir -p /etc/softfire && mkdir -p /etc/softfire/users
COPY etc/experiment-manager.ini /etc/softfire/ 
COPY etc/mapping-managers.json /etc/softfire/
COPY . /app
# RUN pip install nfv-manager
WORKDIR /app
RUN pip install . && python generate_cork_files.py -y /etc/softfire/users && git clone https://github.com/softfire-eu/views.git /etc/softfire/views

EXPOSE 5051
EXPOSE 5080

CMD ./experiment-manager
