from logging import Logger
from collections import namedtuple
import json
import datetime
import os
import psutil
import requests
from bot_logging.threading_queue import send_message, ConsumerThread



HOST_CONFIG_PATH = 'host_config.json'
log_item = namedtuple('log_item', ['level', 'msg', 'datetime'])

class ServerSender():
    def __init__(self, url, credientals):
        self.url = url

    def send(self, data):
        r = requests.post(self.url)

class TestSender():
    def __init__(self):
        pass

    def send(self, data):
        print(f'[sender] {data}')
        return True

sender = TestSender()
consumer = ConsumerThread(sendDBfn=sender.send)
consumer.start()

class TelegramLogger(Logger):
    def __init__(self, process_user_desc, level=0,
                 post_min_level = 40,
                 post_batch_size = 20,
                 post_min_time_freq = 5.0,
                 post_max_size = -1,
                 max_cache_size = 1000,
                 **kwargs):

        Logger.__init__(self, "TBL", level)

        pid = os.getpid()
        process = psutil.Process(pid)
        self.info = {
            'process_user_desc': process_user_desc,
            'pid': pid,
            'process_name': process.name()
        }

        self.post_min_level = post_min_level
        self.post_batch_size = post_batch_size
        self.post_min_freq = post_min_time_freq
        self.post_max_size = post_max_size
        self.max_cache_size = max_cache_size

        #self.host_config = json.load(open(HOST_CONFIG_PATH, 'r'))
        #HOST_CONFIG_KEYS = ['private_key', 'server_ip', 'server_port', 'host_name']
        #for key in HOST_CONFIG_KEYS:
        #   assert key in self.host_config, f"No {key} in {HOST_CONFIG_PATH}"

        self.last_post_time = datetime.datetime.now()

        self.post_worker = self.init_post_worker()

    #TODO
    def init_post_worker(self):
        thread = None
        return thread

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        #Logger._log(self, level, '[LBL] ' + msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)
        if level  >=  self.post_min_level:
            dt = datetime.datetime.utcnow()
            send_message(log_item(level=level, msg=msg, datetime=dt))

    def post_cache(self):
        if len(self.cache) > 0:
            cache_to_post = []
            try:
                #TODO: lock cache
                if self.post_max_size != -1 and len(self.cache) > self.post_max_size:
                    cache_to_post = self.cache[-self.post_max_size:]
                    self.cache = self.cache[:-self.post_max_size]
                else:
                    cache_to_post = self.cache
                    self.cache = []

                post_json = self.prepare_post_json(cache_to_post)
                self.send(post_json)

                #TODO: lock
                self.last_post_time = datetime.datetime.now()
            except:
                # TODO: lock cache
                self.cache = cache_to_post + self.cache

    def send(self, json, host_config):
        send_message(json)

    def prepare_post_json(self, data):
        res = { 'private_key': self.host_config['private_key'],
                **self.info,
               'data': data,
                #TODO: datetime to str/json
               'post_time': datetime.datetime.utcnow()
               }
        return res

    #def __del__(self):
    #    self.post_worker.kill()
