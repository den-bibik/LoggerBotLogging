import os
import psutil
import datetime


class ServerSender:
    def __init__(self, user_name, user_token, host):
        pid = os.getpid()
        process = psutil.Process(pid)
        self.pid = pid
        self.process_name = process.name()

        self.user_name = user_name
        self.user_token = user_token
        self.host = host


    def send(self, batch_logs):
        # batch_logs =  [ {'level':level, 'msg':msg, 'event_at':msg_datetime, ‘p_description': logger_name}, ...]
        data = {
            'post_time': datetime.datetime.utcnow(),
            'user': self.user_name,
            'user_token': self.user_token,
            'pid': self.pid,
            'process_name': self.process_name,
            'logs': batch_logs
        }

        self._send(data)

    def _send(self, data):
        pass