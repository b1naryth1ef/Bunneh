import sys, os, time

default_poll = lambda: True

class Clock(object):
    def __init__(self, action=None, poll=default_poll, fps=30):
        self.max = fps
        self.poll = poll
        self.action = action
        self.last = 0

    def tick(self):
        while not self.poll():
            time.sleep(1/self.max)
        if self.action: self.action()

