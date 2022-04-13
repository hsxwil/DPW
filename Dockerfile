FROM python:3.8-alpine
WORKDIR /app
RUN pip install pika==1.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV MQ_HOST="localhost" MQ_PORT="5672" MQ_USER="guest" MQ_PASS="guest" MQV_HOST="/"
COPY dpw /app

CMD ["python", "-u", "_main.py"]
