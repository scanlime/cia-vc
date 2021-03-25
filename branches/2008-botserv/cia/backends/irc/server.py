class Server(object):
    def __init__(self, idname, host, port, retcount, interval):
        self.idname = idname
        self.host = host
        self.port = port
        self.retcount = retcount
        self.interval = interval
        self.stale = False
        self.timeout = 0
