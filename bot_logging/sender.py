import requests


class ServerSender:
    def __init__(self, credientals=None):
        if credientals is not None and "url" in credientals:
            self.url = credientals["url"]

    def send(self, data):

        r = requests.post(self.url)

    # def prepare_post_json(self, data):
    #     res = {
    #         "private_key": self.host_config["private_key"],
    #         "data": data,
    #         # TODO: datetime to str/json
    #         "post_time": datetime.datetime.utcnow(),
    #         **self._info,
    #     }
    #     return res