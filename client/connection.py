import sys, os, time
import socket, zlib, json
from lib.lib import Location
from lib.entity import Player
from collections import deque
import thread

port = 1337
prefix = ""
suffix = "\r\n"

class Connection():
    def __init__(self):
        self.ip = None
        self.port = None
        self.name = None
        self.c = None
        self.Q = deque()
        self.actions = {
            'HELLO':self.packet_HELLO,
            'POS':self.packet_POS,
            'ADD_ENT':self.packet_ADDENT,
            'RMV_ENT':self.packet_RMVENT,
            'LIST':self.packet_LIST,
        }

        self.connected = False

    def connect(self, **kwargs):
        if not self.connected:
            self.__dict__.update(kwargs)
            self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.c.connect((self.ip, port))
            c = self.write({'action':'HELLO'}, True)
            if c['data']['slots'] <= 0:
                print "Server is full!"
                return
            c = self.write({'action':'JOIN', 'name':self.name}, True)
            if c['action'] == 'JOIN': 
                self.game.player = Player(name=self.name, id=c['id'], loc=Location(data=c['location']))
                self.game.addPlayer(self.game.player)
                self.game.startLoop()
    
    def loop(self):
        while True:
            try: self.read(parse=2)
            except socket.error: 
                print 'Connection lost!'
                sys.exit()

    def read(self, b=1024, parse=0):
        line = self.c.recv(b)
        if line:
            for line in line.split('\n'):
                if line:
                    print '"'+line.strip()+'"'
                    line = json.loads(line.strip())
                    if parse == 1: self.parse(line)
                    elif parse == 2: self.Q.append(line)
                    else: return line
        else: self.c.close()

    def parse(self, l):
        print 'Parsing:', l.get('action')
        if l.get('action') in self.actions.keys():
            self.actions[l.get('action')](l)

    def write(self, packet, ret=False):
        self.c.send("%s%s%s" % (prefix, json.dumps(packet), suffix))
        if ret: return self.read()

    def packet_LIST(self, packet):
        for i in packet['data']:
            if i['id'] not in self.game.players.keys():
                self.game.addPlayer(Player(data=i))

    def packet_ADDENT(self, packet):
        self.game.addEnt(packet)

    def packet_POS(self, packet):
        self.game.updatePos(packet['id'], Location(data=packet['location']))

    def packet_RMVENT(self, packet):
        if packet['type'] == 'player':
            if packet['id'] in self.game.players.keys():
                self.game.rmvPlayer(packet['id'])

    def packet_HELLO(self, packet):
        self.server_data = packet['data']

