FROM python:3.11-slim

WORKDIR /app
COPY *.py ./

RUN pip install paho-mqtt numpy

CMD ["python", "run.py"]
