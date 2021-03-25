# messages --->:
# start-sync
# syncaddsrv net/serv <retcount>
# syncaddch net/#chan <retcount>
# end-sync
# msg net/#chan <line>
# addch net/chan
# delch net/chan
#
# <--- messages:
# servfail net/serv
# joinfail net/#chan
# kick net/#chan
# [servsucc net/serv]
# joinsucc net/#chan
# names-negotiation...

#
# Core concept for channels (targets) and servers, and backoffs/timeouts:
# A server or channel is, at any given time, "owned" by one of three entities:

# - Its network, if it's awaiting service
# - A bot, if it's attempting to connect there (server)
#       or if it's attempting to join or joined (channel)
# - interface.py, sitting in the backoff or timeout mechanisms
# - not owned by anything, if it fell off the long end of backoffs

# This hopefully simplifies the whole "waiting" concept a bit...
# As it turns out, the only fundamental difference between a channel
# and a server, at this level, is that a channel is only joined once.


# obsolescent, see interface.py

def accept(target, message):
    bots[target].enqueue(message)

def sync_start():
    global requests
    requests = []

def sync_add(network, channel):
    requests.push( (network, channel) )

def sync_end():
    for network in networks:
        for channel in network.channels():
            channel.active = False

    for (network, channel) in requests:
        networks[network].channels[channel].active = True

    for network in networks:
        for channel in network.channels():
            if not channel.active:
                channel.destroy()
        network.check_load()

def add_target(network, channel):
    networks[network].channels[channel].active = True
    networks[network].check_load()

def rem_target(network, channel):
    networks[network].channels[channel].destroy()
    networks[network].check_load()

class TargetNetwork(object):

class Bot(object):
    def __init__(self, sock):
        self.queue = []
        self.blocked = True
        self.connection = sock

    def enqueue(self, message):
        self.queue.push(message)
        self.try_send()

    def try_send(self):
        if self.blocked:
            return


