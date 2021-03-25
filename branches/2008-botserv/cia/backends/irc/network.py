class Network(object):
    def __init__(self, host, port):
        self.servers = {}
        self.readyservers = set()
        self.bots = set()
        self.targets = {}
        self.unfulfilled = set()
        assert self.maxchannels > 0

    def create_bot(self):
        if self.readyservers:
            server = self.readyservers.pop()
            newbot = bot.Bot(self, server)
            self.bots.add(newbot)

    def mark_stale(self):
        for target in self.targets.itervalues():
            target.stale = True
        for server in self.servers.itervalues():
            server.stale = True

    def syncchan(self, channame, retcount):
        if channame in self.targets:
            target = self.targets[channame]
        else:
            target = Target(channame)
            self.targets[channame] = target

        target.retcount = retcount
        target.stale = False

    def flush_stale(self):
        for target in self.targets.values():
            if target.stale:
                target.destroy()
                del targets[target.channame]
                self.unfulfilled.discard(target)
        for server in self.servers.values():
            if server.stale:
                del servers[server.idname]
                self.readyservers.discard(server)


    def create_target(self, channame):
        chan = Target(channame)
        self.targets[channame] = chan
        self.unfulfilled.add(chan)

    def destroy_target(self, channame):
        chan = self.targets.pop(channame)
        self.unfulfilled.discard(chan)
        chan.destroy()

    def want_more_bots(self):
        """True if we know we'll need more bots than we have now."""
        return (self.maxchannels * len(self.bots)) < len(self.targets)

    def activatemany(self):
        """Called once all requests and servers are here.

           This kicks off a wave of bot connects.
           """

        targetsleft = len(self.targets) - self.maxchannels * len(self.bots)
        while targetsleft > 0:
            self.create_bot()
            targetsleft -= self.maxchannels
        # And just in case...
        self.activate()


    def activate(self):
        """Called whenever we may need more bot connections.

           Specifically, when:
            - A bot detects it is full
            - A server has become ready again
              (after potentially a backoff and the connect interval)

           This function often does nothing, except when it's sure we'll need
           more bots, and we have a server ready to connect one to.
        """
        if len(self.unfulfilled) == 0:
           return

        all_full = True
        for bot in self.bots:
           if not bot.is_full():
               all_full = False
           if bot.is_idle():
               bot.activate()
           if len(self.unfulfilled) == 0:
               return

        # Connect another bot if all bots are currently full,
        # or we know that we're going to need more
        # (but not if we can fulfill all requests with what we have, only need
        #  to wait until one or more bots are done joining)
        if all_full or self.want_more_bots():
            self.create_bot()

    def get_todo(self):
        if len(self.unfulfilled) == 0:
            return None
        return self.unfulfilled.pop()
