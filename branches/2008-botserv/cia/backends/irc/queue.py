import collections

class HeadLimitQueue(object):
    """A queue with limited size that keeps the newest messages.

       The next pop after the limit is passed will return the string
       "(42 lines dropped)".
       Unsuitable for high-traffic queues with many pushes and pops
       (too many drop messages), but quite suitable for queues that are first
       only pushed, then only popped.
    """
    # This should be less than the limit on TailLimitQueue
    limit = 5
    droptemplate = "(%d lines omitted)"

    def __init__(self):
        self.queue = collections.deque()
        self.dropped = 0

    def __len__(self):
        if self.dropped:
            # Count the "(42 lines dropped)" message
            return len(self.queue) + 1
        else:
            return len(self.queue)

    def dropstring(self):
        dropped = self.dropped
        self.dropped = 0
        return self.droptemplate % dropped

    def push(self, item):
        if self.dropped or len(self.queue) > self.limit:
            self.dropped += 1
            self.queue.popleft()
        self.queue.put(item)

    def peek(self):
        # If we have a "(XY lines dropped)" entry, fix it so it won't change
        # between peek() and pop()
        if self.dropped:
            self.queue.appendleft(self.dropstring())
        # In any case, it's now queue[0] or IndexError
        return self.queue[0]

    def pop(self):
        if self.dropped:
            return self.dropstring()
        else:
            return self.queue.popleft()

class TailLimitQueue(object):
    """A queue with limited size that keeps the oldest messages.

       When the limit is reached, a special state is entered, in which
       new messages are counted and discarded. This state is kept until
       all messages on the queue, plus one, are popped. This last message
       will be "(42 lines dropped)".
       Suitable for high-traffic queues that see frequent pushes and pops.
    """
    limit = 20
    droptemplate = "(%d lines dropped)"

    def __init__(self):
        self.queue = collections.deque()
        self.dropped = 0

    def __len__(self):
        if self.dropped:
            # Count the "(42 lines dropped)" message
            return len(self.queue) + 1
        else:
            return len(self.queue)

    def dropstring(self):
        dropped = self.dropped
        self.dropped = 0
        return self.droptemplate % dropped

    def push(self, item):
        if self.dropped or len(self.queue) > self.limit:
            self.dropped += 1
        else:
            self.queue.append(item)

    def peek(self. item):
        # is this the "XY dropped" entry?
        if self.dropped and (len(self.queue) == 0):
            # Move it into our queue, so it doesn't change between
            # peek() and a later pop()
            self.push(self.dropstring())

        # In any case, it's now queue[0] or IndexError
        return self.queue[0]

    def pop(self, item):
        if len(self.queue) > 0:
            return self.queue.popleft()
        elif self.dropped:
            return self.dropstring()
        else:
            raise IndexError, "pop from an empty TailLimitQueue"


class FairQueue(object):
    def __init__(self):
        self.queue = collections.deque()
        self.index = {}

    def put(self, key, message):
        if key in index:
            target = index[key]
        else:
            target = TailLimitQueue()
            index[key] = target
            self.queue.append(key)
        target.put(message)

    def peek(self):
        if len(self.queue == 0):
            return None
        key = self.queue[0]
        target = self.index[key]
        return target[0]

    def pop(self):
        key = self.queue.popleft()
        target = self.index[key]
        result = target.pop()
        if len(target) > 0:
            self.queue.append(key)
        else:
            del self.index(key)
        return result
