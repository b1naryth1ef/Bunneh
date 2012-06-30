import json, random
import sys, os, time
from lib.lib import *
from lib.entity import *
from lib.mapper import test
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, task

HOOKS = {}

def Hook(hook):
    def deco(func):
        if hook not in HOOKS.keys():
            HOOKS[hook] = func
            return func
        raise Exception('Duplicate hook!')
    return deco

class Server():
    def __init__(self, name="Test", version=0, max_clients=5):
        self.name = name
        self.version = version
        self.max_clients = max_clients
        self.motd = 'Woooot! Bitches and hoes yo!'
        self.port = 1337

        self.worlds = {
        1:World(1, test)
        }
        self.clients = {}
        self.slots = range(1, self.max_clients+1)

    def getData(self):
        return {
        'slots':len(self.slots),
        'name':self.name,
        'motd':self.motd,
        }

    def getClient(self, cid):
        return self.clients[cid]

    def addClient(self, client):
        if not len(self.slots): return -1
        cid = self.slots.pop(0)
        self.clients[cid] = client
        return cid

    def rmvClient(self, cid):
        print 'Removing client...'
        del self.clients[cid]
        self.slots.append(cid)
      
server = Server()

class RemoteClient(LineReceiver):
    def __init__(self, addr):
        self.addr = addr
        self.lastPong = 0
        self.cid = None
        self.pos = [0, 0]
        self.server = server
        self.hasConnected = False
        self.canMove = False
        self.waitForInfo = False

    def send(self, line):
        print 'Send:> %s' % line
        self.sendLine('%s' % json.dumps(line))

    def connectionMade(self): pass

    def connectionLost(self, reason):
        if self.hasConnected:
            self.server.rmvClient(self.cid)
            for c in self.server.clients.values():
                c.send({'action':'RMV_ENT', 'id':self.cid, 'type':'player'})
        print 'Disconnected: %s' % reason

    def lineReceived(self, line):     
        try:
            line = json.loads(line)
            if HOOKS.get(line['action']):
                HOOKS[line['action']](self, line)
        except Exception, e:
            print 'Was not able to parse line! (%s)' % e
        print ">>> ",line

    def globalSend(self, data, ignore=True):
        for i in self.server.clients.values():
            if i != self or not ignore:
                i.send(data)

    @Hook('ACTION')
    def event_POS(self, packet):
        if packet['type'] == "MOVE":
            lc = Location(data=packet['pos'])
            if lc != self.player.loc and self.canMove and self.server.worlds[self.player.loc.w].level.checkMove(lc):
                self.globalSend({'action':'POS', 'id':self.player.id, 'location':lc.dump()})
                self.player.loc = lc
                return
            self.send({'action':'POS', 'id':self.player.id, 'location':self.player.loc.dump()})

    @Hook('HELLO')
    def event_HELLO(self, packet):
        self.send({'action':'HELLO', 'data':self.server.getData()})

    @Hook('INFO')
    def event_INFO(self, packet):
        self.send({'action':'LIST', 'data':[i.player.dump() for i in self.server.clients.values() if i != self]})
        if self.waitForInfo:
            self.globalSend({'action':'ADD_ENT', 'type':'player', 'data':{'name':self.player.name, 'id':self.cid, 'loc':self.player.loc.dump()}})
            self.waitForInfo = False
            self.canMove = True

    @Hook('JOIN')
    def event_JOIN(self, packet):
        self.cid = self.server.addClient(self)
        pos = Location(x=random.randint(1, 10), y=random.randint(1, 10), w=1)
        self.player = Player(id=self.cid, name=packet['name'], loc=pos)#self.server.worlds[1].start.dump())
        self.hasConnected = True
        if self.cid != -1:
            self.send({'action':'JOIN', 'id':self.cid, 'location':self.player.loc.dump()})
            self.waitForInfo = True
        else:
            self.send({'action':'KICK', 'reason':(0, 'Server is full!')})
            self.transport.loseConnection()

    @Hook('PONG')
    def event_PONG(self, packet):
        self.lastPong = time.time()

    def action_KICK(self, reason):
        self.send({'action':'KICK', 'reason':reason})
        self.transport.loseConnection()

class Host(Factory):
    def buildProtocol(self, addr):
        return RemoteClient(addr)

def start():
    reactor.listenTCP(server.port, Host())
    reactor.run()