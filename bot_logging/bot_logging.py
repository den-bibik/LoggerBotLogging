from logging import Logger
from collections import namedtuple
from .threading_queue import ProducerHandler
from .sender import ServerSender
import os


HOST_CONFIG_PATH = "host_config.json"
log_item = namedtuple("log_item", ["level", "msg", "datetime"])


class RemoteLogger(Logger):
    """
    Use this class instead Logger to send your logs to server
    """

    def __init__(
        self,
        logger_name,
        user_name=None,
        host=None,
        sender=None,
        max_batch=30,
        min_batch=10,
        max_history_len=200,
        max_time2update=5.0,
        **kwargs
    ):
        """
        :param logger_name: name for current logger
        :param user_name: for authentication
        :param host: for authentication
        :param sender: used only for non ServerSender. For example for test use TestSender
        :param max_batch: sending params
        :param min_batch: sending params
        :param max_history_len: max size for query
        :param max_time2update: send batch with size less then min_batch
        :param kwargs:
        """
        if sender is None:
            assert isinstance(user_name, str), "user_name must be string"
            assert isinstance(host, str), "host must be string"
            user_token = os.environ["LOGGER_TOKEN"]
            sender = ServerSender(user_name, user_token, host)
        Logger.__init__(self, "TBL " + logger_name, **kwargs)
        handler = ProducerHandler(
            sender,
            logger_name,
            max_batch=max_batch,
            min_batch=min_batch,
            max_history_len=max_history_len,
            max_time2update=max_time2update,
            level=self.level,
        )
        self.addHandler(handler)
