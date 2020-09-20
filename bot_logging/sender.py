import os
import psutil
import datetime

from .threading_queue import Singleton


class SenderBase(metaclass=Singleton):
    def __init__(self):
        pid = os.getpid()
        process = psutil.Process(pid)
        self.pid = pid
        self.process_name = process.name()

    def send(self, batch_logs):
        # batch_logs =  [ {'level':level, 'msg':msg, 'event_at':msg_datetime, ‘p_description': logger_name}, ...]
        # return True in case of success

        data = {
            'post_time': datetime.datetime.utcnow(),
            'pid': self.pid,
            'process_name': self.process_name,
            'logs': batch_logs
        }
        return self._send(data)

    def _send(self, data):
        raise NotImplementedError()

class ServerSender(SenderBase):
    def __init__(self, user_name, user_token, host):
        SenderBase.__init__(self)
        self.user_name = user_name
        self.user_token = user_token
        self.host = host

    def _send(self, data):
        data['user'] = self.user_name
        data['user_token'] = self.user_token
        #TODO: send to server
        return False

class TestSender(SenderBase):
    def __init__(self):
        SenderBase.__init__(self)
        self.data = []

    def _send(self, data):
        self.data.append(data)
        return True