class Bot(object):
    def __init__(self, network, server):
        self.conn = None
        self.network = network
        self.server = server
        self.trying = "connecting"
        self.channels = set()
        self.queue = queue.FairQueue()
        #d = connect(server, MyIrcProto)
        #d.addCallbacks(self.connect_done, self.connect_failed)

    def connect_done(self, conn):
        """Called when the IRC connection is fully estabilished (!)

           The assumption is that we can join channels when this is called,
           and any failure in the connection past this point cannot be
           reliably attributed to a failure of that specific server,
           and so should have no influence on our backoff mechanism.

           When this gets called, the server we're connecting to becomes
           eligible again for re-connection.
           """
        self.trying = None
        self.conn = conn
        interface.srv_succ(self.server)
        self.next()

    def connect_failed(self, fail):
        self.trying = "unable to connect"
        interface.srv_fail(self.server, fail)
        self.network.drop_bot(self)

    def is_idle(self):
        return ((self.trying is None) and not self.is_full())

    def is_full(self):
        # TODO: Add recognition of the appropriate numerics as well
        return (len(self.channels) >= self.network.maxchannels)

    def next(self):
        """Called when we've finished our current pending-join.
           Will either get another channel to join if we can,
           or tell the network to re-check if we need more bots.
        """
        if self.is_full():
            self.network.activate()
        else:
            self.activate()

    def activate(self):
        assert self.is_idle()
        self.trying = self.network.get_todo()
        if not self.trying:
            return
        # XXX - conn.join(self.trying)
        # TODO: add timeout

    def join_success(self, target):
        assert self.trying == target
        target.set_bot(self)
        interface.join_succ(target)
        self.channels.add(target)
        self.trying = None
        self.next()

    def join_fail(self, target, reason):
        self.trying = None
        interface.join_fail(target, reason)
        self.next()

    def message(self, target, message):
        self.queue.put(target, message)
        # XXX self.conn.poke_send
