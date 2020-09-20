class TestSender:
    def __init__(self):
        self.data = []

    def send(self, batch):
        self.data.append(batch)
        return True
