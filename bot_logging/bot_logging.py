from logging import Logger
from collections import namedtuple
import json
import datetime
import os
import psutil

from .threading_queue import send_message, ConsumerThread
from .sender import ServerSender


HOST_CONFIG_PATH = "host_config.json"
log_item = namedtuple("log_item", ["level", "msg", "datetime"])

class TelegramLogger(Logger):
    def __init__(
        self,
        process_user_desc,
        level=0,
        post_min_level=40,
        post_batch_size=20,
        post_min_time_freq=5.0,
        post_max_size=-1,
        max_cache_size=1000,
        sender = ServerSender(),
        **kwargs
    ):

        self.consumer = ConsumerThread(sendDBfn=sender.send)
        self.consumer.mutex_producer_number.acquire()
        if self.consumer.first_producer:
            self.consumer.first_producer = False
        else:
            self.consumer.producer_number += 1

        self.consumer.mutex_producer_number.release()


        Logger.__init__(self, "TBL", level, **kwargs)
        pid = os.getpid()
        process = psutil.Process(pid)
        self._info = {
            "process_user_desc": process_user_desc,
            "pid": pid,
            "process_name": process.name(),
        }

        self._post_min_level = post_min_level
        self._post_batch_size = post_batch_size
        self._post_min_freq = post_min_time_freq
        self._post_max_size = post_max_size
        self._max_cache_size = max_cache_size
        self._sender = sender

        # self.host_config = json.load(open(HOST_CONFIG_PATH, 'r'))
        # HOST_CONFIG_KEYS = ['private_key', 'server_ip', 'server_port', 'host_name']
        # for key in HOST_CONFIG_KEYS:
        #   assert key in self.host_config, f"No {key} in {HOST_CONFIG_PATH}"

        self.last_post_time = datetime.datetime.now()

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        # Logger._log(self, level, '[LBL] ' + msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)
        if level >= self._post_min_level:
            dt = datetime.datetime.utcnow()
            send_message(log_item(level=level, msg=msg, datetime=dt))

    def send(self, json, host_config):
        send_message(json)

    def prepare_post_json(self, data):
        res = {
            "private_key": self.host_config["private_key"],
            "data": data,
            # TODO: datetime to str/json
            "post_time": datetime.datetime.utcnow(),
            **self._info
        }
        return res

    def __del__(self):
        self.consumer.mutex_producer_number.acquire()
        self.consumer.producer_number -= 1
        print('self.consumer.producer_number', self.consumer.producer_number)
        self.consumer.mutex_producer_number.release()