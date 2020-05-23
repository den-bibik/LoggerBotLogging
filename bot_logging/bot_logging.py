from logging import Logger
from collections import namedtuple
import json
import datetime
import os
import psutil


HOST_CONFIG_PATH = 'host_config.json'
log_item = namedtuple('log_item', ['level', 'msg', 'datetime'])

class TelegramLogging(Logger):
    def __init__(self, name, process_user_desc,
                 post_min_level = 40,
                 post_batch_size = 20,
                 post_min_time_freq = 5.0,
                 post_max_size = -1,
                 max_cache_size = 1000):

        Logger.__init__(self, name)

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

        self.host_config = json.load(HOST_CONFIG_PATH)
        HOST_CONFIG_KEYS = ['private_key', 'server_ip', 'server_port', 'host_name']
        for key in HOST_CONFIG_KEYS:
            assert key in self.host_config, f"No {key} in {HOST_CONFIG_PATH}"

        self.last_post_time = datetime.datetime.now()
        self.cache = []

        self.post_worker = self.init_post_worker()

    #TODO
    def init_post_worker(self):
        thread = None
        return thread

    def log(self, level, msg, *args, **kwargs):
        dt = datetime.datetime.now()
        if level  >=  self.post_min_level:
            self.cache.append(log_item(level=level, msg=msg, datetime=dt))
        Logger.log(self, level, msg, *args, **kwargs)

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
        pass

    def prepare_post_json(self, data):
        res = { 'private_key': self.host_config['private_key'],
                **self.info,
               'data': data,
                #TODO: datetime to str/json
               'post_time': datetime.datetime.now()
               }
        return res

    def __del__(self):
        self.post_worker.kill()
        self.post_cache()