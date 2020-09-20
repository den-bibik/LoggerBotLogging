from logging import Logger
from collections import namedtuple
import json
import datetime
import os
import psutil

from .threading_queue import Producer
from .sender import ServerSender


HOST_CONFIG_PATH = "host_config.json"
log_item = namedtuple("log_item", ["level", "msg", "datetime"])



class RemoteLogger(Logger, Producer):
    def __init__(
        self,
        process_user_desc,
        sender=ServerSender(),
        **kwargs
    ):
        Producer.__init__(self, sender.send)
        Logger.__init__(self, "TBL", **kwargs)

        pid = os.getpid()
        process = psutil.Process(pid)
        self._info = {
            "process_user_desc": process_user_desc,
            "pid": pid,
            "process_name": process.name(),
        }


    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if level >= self.level:
            dt = datetime.datetime.utcnow()
            self._send(log_item(level=level, msg=msg, datetime=dt))
