from logging import Logger
from collections import namedtuple
from .threading_queue import ProducerHandler
from .sender import ServerSender
import os


HOST_CONFIG_PATH = "host_config.json"
log_item = namedtuple("log_item", ["level", "msg", "datetime"])



class RemoteLogger(Logger):
    def __init__(
        self,
        process_user_desc,
        user_name=None,
        host=None,
        sender=None,
        **kwargs
    ):
        if sender is None:
            assert isinstance(user_name, str), "user_name must be string"
            assert isinstance(host, str), "host must be string"
            user_token = os.environ['LOGGER_TOKEN']
            sender = ServerSender(user_name, user_token, host)
        Logger.__init__(self, "TBL " + process_user_desc, **kwargs)
        handler = ProducerHandler(sender, process_user_desc, level = self.level)
        self.addHandler(handler)
