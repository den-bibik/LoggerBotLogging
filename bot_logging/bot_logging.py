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




sender = ServerSender()
consumer = ConsumerThread(sendDBfn=sender.send)
consumer.start()


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
        sender = sender,
        **kwargs
    ):

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
        self.post_worker = self.init_post_worker()

    # TODO
    def init_post_worker(self):
        thread = None
        return thread

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        # Logger._log(self, level, '[LBL] ' + msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)
        if level >= self._post_min_level:
            dt = datetime.datetime.utcnow()
            send_message(log_item(level=level, msg=msg, datetime=dt))

    def post_cache(self):
        if len(self.cache) > 0:
            cache_to_post = []
            try:
                # TODO: lock cache
                if self._post_max_size != -1 and len(self.cache) > self._post_max_size:
                    cache_to_post = self.cache[-self._post_max_size:]
                    self.cache = self.cache[: -self._post_max_size]
                else:
                    cache_to_post = self.cache
                    self.cache = []

                post_json = self.prepare_post_json(cache_to_post)
                self.send(post_json)

                # TODO: lock
                self.last_post_time = datetime.datetime.now()
            except:
                # TODO: lock cache
                self.cache = cache_to_post + self.cache

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
       self.post_worker.kill()
