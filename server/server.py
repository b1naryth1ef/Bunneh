import json, random
import sys, os, time
import database
import groups
from lib.lib import *
from lib.entity import *
from lib.mapper import test
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, task, defer

HOOKS = {}
debug = False

def Hook(hook):
    def deco(func):
        if hook not in HOOKS.keys():
            HOOKS[hook] = func
            return func
        raise Exception('Duplicate hook!')
    return deco

def compMessage(msg):
    print 'Compressing: %s' % msg
    return zlib.compress(json.dumps(msg))

class Server():
    def __init__(self, name="Test", version=0, max_clients=5):
        self.name = name
        self.version = version
        self.max_clients = max_clients
        self.motd = 'Woooot! Bitches and hoes yo!'
        self.port = 1337
        self.version = 2

        self.worlds = {
            1:World(1, levels={1:Level(1, test)})
        }

        self.clients = {}
        self.slots = range(1, self.max_clients+1)

        self.addEntity('LOVE_BUNNY', Location(data=[1, 1, 1, 1]))

    def getLevel(self, pos):
        return self.worlds[pos.w].levels[pos.l]

    def players(self):
        return [i.player for i in self.clients.values()]

    def getNearestPlayer(self, pos):
        dist = []
        avail = [i for i in self.players() if i.pos.w == pos.w and i.pos.l == pos.l]
        for obj in avail:
            d = pos.distance(obj.pos)
            if len(dist):
                if d > dist[0]: continue
            dist = [d, obj]
        if len(dist):
            return dist[1]

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

    def findByName(self, name):
        for cli in self.clients.values():
            if name in cli.player.name:
                return cli

    def addEntity(self, typ, pos):
        id = 0
        while id in self.getLevel(pos).ents.keys():
            id = random.randint(10e5, 10e6)
        m = mob_types[typ](eid=id, pos=pos, server=self)
        self.getLevel(pos).addEnt(m)
        self.globalSend({'action':'ADD_ENT', 'type':'mob', 'data':m.dump()})

    def rmvEntity(self, entid): pass

    def globalSend(self, msg):
        msg = compMessage(msg)
        for o in self.clients.values():
            o.sendLine(msg)

    def tick(self):
        for i in self.worlds.values():
            for l in i.levels.values():
                for e in l.ents.values():
                    e.tick()
      
server = Server()

class RemoteClient(LineReceiver):
    def __init__(self, addr):
        self.dbid = -1
        self.addr = addr
        self.lastPong = 0
        self.cid = None
        self.server = server
        self.hasConnected = False
        self.waitForInfo = False
        self.lastMove = 0

        self.lastRecv = 0

        self.group = groups.NewbLevel

    def getCurrentLevel(self):
        return self.server.worlds[self.player.pos.w].levels[self.player.pos.l]

    def send(self, line):
        print 'Send:> %s' % line
        self.sendLine(zlib.compress(json.dumps(line)))

    def connectionMade(self): pass

    def connectionLost(self, reason):
        if self.hasConnected:
            if self.dbid != -1:
                obj = database.getUserByID(self.dbid)
                obj.pos = self.player.pos.dumps()
                obj.save()
            self.server.rmvClient(self.cid)
            for c in self.server.clients.values():
                c.send({'action':'RMV_ENT', 'id':self.cid, 'type':'player'})
        print 'Disconnected: %s' % reason

    def lineReceived(self, line):
        if not self.hasConnected:   
            if time.time()-self.lastRecv > .02:
                self.lastRecv = time.time()
            else: time.sleep(.05)
        if 1==1: #try:
            line = json.loads(zlib.decompress(line))
            if HOOKS.get(line['action']):
                HOOKS[line['action']](self, line)
        #except Exception, e:
        #    print 'Was not able to parse line! (%s)' % e
        if debug: print ">>> ",line

    def globalSend(self, data, ignore=True):
        data = compMessage(data)
        for i in self.server.clients.values():
            if i != self or not ignore:
                i.send(data)

    @Hook('ACTION')
    def event_POS(self, packet):
        if packet['type'] == "MOVE":
            if self.group.canMove:
                lc = Location(data=packet['pos'])
                m = checkMove(self.player, lc, self.getCurrentLevel().map)
                if lc != self.player.pos and m and time.time()-self.lastMove > self.group.moveThrottle:
                    self.lastMove = time.time()
                    self.globalSend({'action':'POS', 'id':self.player.id, 'location':lc.dump()})
                    self.player.pos = lc
                    return
            self.send({'action':'POS', 'id':self.player.id, 'location':self.player.pos.dump()})
        elif packet['type'] == 'MSG':
            if self.group.canTalk:
                self.globalSend({'action':'MSG', 'data':packet['data'], 'id':self.cid}, False)
        elif packet['type'] == 'CMD':
            if self.group.canCmd: pass

    @Hook('HELLO')
    def event_HELLO(self, packet):
        self.send({'action':'HELLO', 'data':self.server.getData()})

    @Hook('INFO')
    def event_INFO(self, packet):
        self.send({'action':'LIST', 'data':[i.player.dump() for i in self.server.clients.values() if i != self]})
        if self.waitForInfo:
            self.globalSend({'action':'ADD_ENT', 'type':'player', 'data':{'name':self.player.name, 'id':self.cid, 'loc':self.player.pos.dump()}})
            self.waitForInfo = False

    @Hook('JOIN')
    def event_JOIN(self, packet):
        if not packet['name']:
            return self.kick('Invalid Nickname!')
        if packet['version'] != self.server.version:
            return self.kick("Protocol mismatch! (You have %s and we have %s)" % (packet['version'], self.server.version))
        if self.server.findByName(packet['name']):
            return self.kick('That user is already joined!')
        self.cid = self.server.addClient(self)
        if self.cid != -1:
            self.player = Player(eid=self.cid, name=packet['name'], pos=self.server.worlds[1].start.dump())
            self.hasConnected = True #This is really used for rmv objects. Dont move it plz!
            obj = database.getUser(self, packet['hash'])
            if type(obj) is str:
                self.kick(obj)
            elif obj is not None:
                self.dbid = obj.id
                self.player.pos = Location().loads(obj.pos)
                for world in self.server.worlds.values():
                    self.send({'action':'WORLD', 'obj':world.dump()})
                    #self.sendLine('\x01'+)
                self.send({'action':'JOIN', 'id':self.cid, 'obj':self.player.dump(), 'hash':obj.hashkey})
                self.waitForInfo = True
            else:
                self.kick('Join Error!')
        else:
            return self.kick('Server is full!')

    @Hook('PING')
    def event_PONG(self, packet):
        self.send({'action':packet.get('respkey', 'PONG'), 'data':time.time()})

    def kick(self, reason):
        self.send({'action':'KICK', 'reason':reason})
        self.transport.loseConnection()

class Host(Factory):
    def buildProtocol(self, addr):
        return RemoteClient(addr)

def start():
    a = task.LoopingCall(f=server.tick)
    a.start(.1)
    reactor.listenTCP(server.port, Host())
    reactor.run()