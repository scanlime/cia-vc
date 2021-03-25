class Target(object):
    def __init__(self, network, channame):
        self.network = network
        self.channame = channame
        self.bot = None
        self.queue = queue.HeadLimitQueue()
        self.stale = False
        self.retcount = 0

    def set_bot(self, bot):
        self.bot = bot
        while len(self.queue) > 0:
            bot.send(self, self.queue.pop())
        del self.queue

    def lose_bot(self):
        self.bot = None
        self.queue = queue.HeadLimitQueue()

    def send(self, message):
        if self.bot:
            self.bot.message(self, message)
        else:
            self.queue.add(message)
