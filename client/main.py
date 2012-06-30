from clib.pygcurse import PygcurseWindow
from clib.inputlib import KeyboardInput
from clib.const import *
from lib.lib import World
from lib.mapper import test
from lib.entity import Player
from connection import Connection
from display import Display

import pygame, thread
import sys, os, time

win = PygcurseWindow(80, 60, fullscreen=False, fontsize=14)
conn = Connection()
inp = KeyboardInput()

pygame.display.set_caption('Bunneh')

class Game():
	def __init__(self):
		self.win = win
		self.conn = conn
		self.disp = Display(win, self)
		self.inp = inp
		self.running = False
		self.worlds = {
		1:World(1, test)
		}

		self.players = {}

	def updatePos(self, cid, loc):
		self.players[cid].pos = loc
		self.disp.updaterender = True

	def addPlayer(self, plyr):
		self.players[plyr.id] = plyr
		self.disp.updaterender = True

	def rmvPlayer(self, plyr):
		del self.players[plyr]
		self.disp.updaterender = True

	def addEnt(self, data):
		if data['type'] == 'player':
			self.players[data['data']['id']] = Player(**data['data'])
		self.disp.updaterender = True

	def startup(self):
		self.conn.connect(game=self, ip=self.win.input("Server IP: ", 0, 0, fgcolor=BLUE), name=self.win.input("Username: ", 0, 0, fgcolor=BLUE))

	def startLoop(self):
		thread.start_new_thread(self.conn.loop, ())
		self.running = True
		self.conn.write({'action':'INFO'})
		while True:
			time.sleep(1/30)
			self.disp.render()
			if len(self.conn.Q):
				self.conn.parse(self.conn.Q.popleft())


g = Game()
g.startup()