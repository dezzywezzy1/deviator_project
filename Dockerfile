FROM ubuntu:22.04

WORKDIR /deviator

RUN apt-get update && apt-get install -y python3.10 python3-pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--debug"]

