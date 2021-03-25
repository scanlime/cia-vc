control = magical()


MAX_BACKOFF = 14
onhold = []
for i in xrange(MAX_BACKOFF):
    onhold[i] = []
hold_counter = 0

networks = {}

def sync_start():
    """Protocol message: start of a sync-active-targets stream."""
    for network in networks.itervalues():
        network.mark_stale()

def sync_srv(net, serv, retcount):
    """Protocol: notifies us what server to use for a given network
       and how bad our experience with it was so far."""
    networks[net].syncserv(serv, retcount)

def sync_chan(net, channame, retcount):
    """Protocol: tells us about a target we should be on, and how bad
       our experience with it was."""
    networks[net].syncchan(channame, retcount)

def sync_end():
    """Protocol: end of sync. Anything not mentioned between sync_start
       and here can be assumed to be stale and can be discarded.

       Will also trigger a recheck of our connected bots on all networks."""
    for network in networks.itervalues():
        network.flush_stale()
        network.activatemany()

def message(net, channame, message):
    """Send a message to a given target.
       Normally, the target will exist, though in some race conditions
       (overlap KICK/message) it's possible that it won't.
       """
    network = networks[net]
    channel = network[channame]
    channel.send(message)

def add_chan(net, chan):
    network = networks[net]
    network.create_target(chan)

def del_chan(net, chan):
    network = networks[net]
    network.destroy_target(chan)

# =====
def srv_succ(server):
    control.srv_succ(server.idname)
    server.retcount = 0
    server.timeout = server.interval
    tickingservers.add(server)


def srv_fail(server, reason):
    control.srv_fail(server.idname, server.retcount, reason)
    if server.retcount >= MAX_BACKOFF:
        return

    hold_srv[server.retcount].add(server)
    server.retcount += 1


def chan_succ(channel):
    control.chan_succ(channel.name)
    channel.retcount = 0


def chan_fail(channel, message):
    control.chan_fail(channel.name, channel.retcount, message)
    if channel.retcount >= MAX_BACKOFF:
        # channel should no longer be referenced after this.
        return

    onhold[channel.retcount].add(channel)
    channel.retcount += 1


def tick():
    check_intervals()
    check_hold() # Potentially only every N ticks


def check_intervals():
    """Checks all server connect intervals.

       Re-adds those servers whose intervals expired.
       """
    checking = tickingservers
    tickingservers = []
    for server in checking:
        if server.timeout:
            server.timeout -= 1
            tickingservers.add(server)
        else:
            network = server.network
            network.act_srv(server)
            network.activate()


def check_hold():
    # Cute hack, what's it do?
    # Well, it essentially looks at the carry bits in addition.
    # In effect, a higher-order bit will flip half as often as a
    # lower-order bit, such that we get a nice exponential progression
    # in re-queue time.
    old_holdcounter = hold_counter
    hold_counter += 1
    carries = old_holdcounter ^ hold_counter

    reactivate_networks = set()

    for i in xrange(MAX_BACKOFF):
        if not (carries & (1<<i)):
            continue
        requeue = onhold[i]
        onhold[i] = []
        for target in requeue:
            network = target.network
            network.add(target)
            reactivate_networks.add(network)

    for network in reactivate_networks:
        network.activate()
