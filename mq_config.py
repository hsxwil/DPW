# -*- coding:utf-8 -*-
# @Date      :2021/4/23
# @Author    :Maoxian
import os

mq_conn = {
    "host": os.getenv("MQ_HOST", "localhost"),
    "port": int(os.getenv("MQ_PORT", "5672")),
    "user": os.getenv("MQ_USER", "guest"),
    "pass": os.getenv("MQ_PASS", "guest"),
    "v_host": os.getenv("MQ_VHOST", "/")
}

mq_exchange = os.getenv("MQ_EXCHANGE", "MEC")