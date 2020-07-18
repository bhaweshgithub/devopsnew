FROM ubuntu:18.04

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install python3 wget unzip jq python3-pip -y
RUN pip3 install boto3
RUN pip3 install awscli

RUN wget https://releases.hashicorp.com/terraform/0.12.3/terraform_0.12.3_linux_amd64.zip
RUN unzip terraform_0.12.3_linux_amd64.zip
RUN mv terraform /bin
RUN chmod +x /bin/terraform
RUN mkdir /provision
WORKDIR /provision

COPY init.py /provision
COPY import.sh /provision
RUN chmod +x /provision/import.sh

CMD python3 ./init.py
