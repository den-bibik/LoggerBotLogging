from logging import Logger
from collections import namedtuple
from .threading_queue import ProducerHandler
from .sender import ServerSender
import os

log_item = namedtuple("log_item", ["level", "msg", "datetime"])

DEFAULT_MAX_BATCH = 30
DEFAULT_MIN_BATCH = 10
DEFAULT_MAX_HISTORY_LEN = 200
DEFAULT_MAX_TIME_TO_UPDATE = 5.0


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
        max_batch=DEFAULT_MAX_BATCH,
        min_batch=DEFAULT_MIN_BATCH,
        max_history_len=DEFAULT_MAX_HISTORY_LEN,
        max_tim_to_update=DEFAULT_MAX_TIME_TO_UPDATE,
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
        :param max_tim_to_update: send batch with size less then min_batch
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
            max_time_to_update=max_tim_to_update,
            level=self.level,
        )
        self.addHandler(handler)
