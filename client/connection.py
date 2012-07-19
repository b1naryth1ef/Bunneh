import sys, os, time
import socket, zlib, json
from lib.lib import Location, World
from lib.entity import Player
from collections import deque
import thread, zlib

version = 2
port = 1337
prefix = ""
suffix = "\r\n"
hashpath = os.path.join(os.getcwd(), '.hashes')

class Connection():
    def __init__(self):
        self.ip = None
        self.port = None
        self.name = None
        self.c = None
        self.Q = deque()
        self.actions = {
            'HELLO':self.packet_HELLO,
            'JOIN':self.packet_JOIN,
            'POS':self.packet_POS,
            'ENT_POS':self.packet_ENTPOS,
            'ADD_ENT':self.packet_ADDENT,
            'RMV_ENT':self.packet_RMVENT,
            'LIST':self.packet_LIST,
            'MSG':self.packet_MSG,
            'KICK':self.packet_KICK,
            'WORLD':self.packet_WORLD,
        }
        self.server_data = {}
        self.connected = False
        self.connecting = False

    def setupHash(self):
        self.curhash = None
        self.hashname = '.%s_%s' % (self.ip, self.name)

        if os.path.exists(hashpath):
            if self.hashname in os.listdir(hashpath):
                with open(os.path.join(hashpath, self.hashname)) as f:
                    self.curhash = f.read()
        else: os.mkdir(hashpath)

    def disconnect(self):
        with open(os.path.join(hashpath, self.hashname), 'w') as f:
            f.write(self.curhash)

    def connect(self, **kwargs):
        if not self.connected:
            self.__dict__.update(kwargs)
            self.setupHash()
            self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.c.connect((self.ip, port))
            self.write({'action':'HELLO'})
            self.connecting = True
            while self.connecting:
                self.read()
    
    def loop(self):
        while True:
            try: self.read(parse=1)
            except socket.error: 
                print 'Connection lost!'
                sys.exit()

    def read(self, b=1024, parse=0):
        line = self.c.recv(b)
        if line:
            for line in line.split('\r\n'):
                if line:
                    line = zlib.decompress(line)
                    print '"'+line.strip()+'"'
                    line = json.loads(line.strip())
                    if parse == 0: self.parse(line)
                    elif parse == 1: self.Q.append((line, time.time()))
                    else: return line
        else: self.c.close()

    def parse(self, l):
        print 'Parsing:', l.get('action')
        if l.get('action') in self.actions.keys():
            self.actions[l.get('action')](l)

    def write(self, packet, ret=False):
        self.c.send("%s%s%s" % (prefix, zlib.compress(json.dumps(packet)), suffix))
        if ret: return self.read()

    def packet_AUTHED(self, packet): pass

    def packet_JOIN(self, packet):
        if self.connecting:
            self.curhash = packet['hash']
            self.game.player = Player(data=packet['obj'])
            self.game.addPlayer(self.game.player)
            self.connecting = False
            self.connected = True
            return self.game.startLoop()

    def packet_HELLO(self, packet):
        if not self.connecting: return
        if packet['data']['slots'] <= 0:
            raise Exception('Server is full!')
            self.connecting = False
            return
        self.server_data = packet['data']
        self.write({'action':'JOIN', 'name':self.name, 'hash':self.curhash, "version":version})

    def packet_LIST(self, packet):
        for i in packet['data']:
            if i['id'] not in self.game.players.keys():
                self.game.addPlayer(Player(data=i))

    def packet_ADDENT(self, packet):
        self.game.addEnt(packet)

    def packet_POS(self, packet):
        self.game.updatePos(packet['id'], Location(data=packet['location']))

    def packet_ENTPOS(self, packet):
        self.game.updateEntPos(packet['id'], Location(data=packet['loc']))

    def packet_RMVENT(self, packet):
        if packet['type'] == 'player':
            if packet['id'] in self.game.players.keys():
                self.game.rmvPlayer(packet['id'])

    def packet_MSG(self, packet):
        self.game.addChat((packet['id'], packet['data']))

    def packet_KICK(self, packet):
        raise Exception(packet['reason'])

    def packet_ZLIB(self, packet):
        pack = json.loads(zlib.decompress(packet['data']))
        self.parse(pack)

    def packet_WORLD(self, packet):
        w = World(data=packet['obj'])
        self.game.worlds[w.id] = w