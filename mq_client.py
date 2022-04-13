import pika
import json
from pika.exceptions import *
from mq_config import mq_conn, mq_exchange
from logconfig import logger


class MQ:
    def __init__(self, queueName):
        self.queue = queueName
        self.MQbody = None
        self.channel = None
        self.connection = None

        self.connect()

    def connect(self):
        try:
            # 重连
            if self.connection and not self.connection.is_closed:
                self.connection.close()

            user_pwd = pika.PlainCredentials(mq_conn["user"], mq_conn["pass"])
            connectparam = pika.ConnectionParameters(
                mq_conn["host"],
                mq_conn["port"],
                mq_conn["v_host"],
                credentials=user_pwd,
                heartbeat=30,
            )
            self.connection = pika.BlockingConnection(connectparam)
            self.channel = self.connection.channel()
        except Exception as e:
            logger.error(e)

    def declare(self, arguments):
        # 初始队列声明
        try:
            self.channel.queue_declare(queue=self.queue, arguments=arguments)
        except Exception as e:
            logger.error("队列{}已存在，且与定义的不一致，将重新声明".format(self.queue))
            self.connect()
            self.channel.queue_delete(self.queue)
            self.channel.queue_declare(queue=self.queue, arguments=arguments)

    def queue_bind(self, exchange, routing_key, arguments=None):
        # 绑定 exchange
        try:
            self.channel.queue_bind(self.queue, exchange, routing_key, arguments)
        except Exception as e:
            logger.error(e)
            self.connect()
            self.channel.exchange_declare(exchange=mq_exchange, durable=True,
                                          exchange_type='topic')
            self.channel.queue_bind(self.queue, exchange, routing_key, arguments)


class MQC(MQ):
    """消费者"""

    def __init__(self, queueName):
        super(MQC, self).__init__(queueName)
        self.declare(arguments={"x-max-length": 1000})

    def callback(self, ch, method, properties, body):
        try:
            self.MQbody = json.loads(body, strict=False)
        except json.decoder.JSONDecodeError:
            self.MQbody = None
            return self.MQbody
        return self.MQbody

    def consuming(self):
        try:
            self.channel.basic_consume(
                queue=self.queue, on_message_callback=self.callback, auto_ack=True
            )
            self.channel.start_consuming()
        except (ChannelClosed, ConnectionClosed) as e:
            logger.error(e)
            self.connect()  # 重连
            self.channel.start_consuming()

    def getMQ(self):
        return self.MQbody


class MQP(MQ):
    """生产者"""

    def __init__(self, queueName):
        super(MQP, self).__init__(queueName)
        self.channel.exchange_declare(exchange=mq_exchange, durable=True,
                                      exchange_type='topic')

    def provideMQ(self, mqbody):
        try:
            self.channel.basic_publish(exchange=mq_exchange, routing_key='TOPIC.7F010001.*',
                                       body=str(mqbody))  # 发的消息
        except Exception as e:
            logger.error(e)
            self.connect()  # 重连
            self.channel.basic_publish(exchange=mq_exchange, routing_key='TOPIC.7F010001.*',
                                       body=str(mqbody))

        self.MQbody = mqbody
        return self.MQbody
