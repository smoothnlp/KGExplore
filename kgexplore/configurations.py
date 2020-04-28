

class Config():

    def __init__(self):
        self.HOST = "http://api.smoothnlp.com"
        self.apikey = None

    def setHost(self,host):
        self.HOST = host

    def setApiKey(self,apikey):
        self.apikey = apikey

config = Config()