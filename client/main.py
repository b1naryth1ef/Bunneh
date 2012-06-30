from clib.pygcurse import PygcurseWindow
from clib.inputlib import KeyboardInput
from clib.const import *
from lib.lib import World, Location
from lib.mapper import test
from lib.entity import Player
from connection import Connection
from display import Display

import pygame, thread, random
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

	def move(self, new):
		if self.worlds[self.player.loc.w].level.checkMove(new):
			self.player.loc = new
			self.conn.write({'action':'ACTION', 'type':'MOVE', 'pos':new.dump()})  
			self.disp.updaterender = True

	def updatePos(self, cid, loc):
		self.players[cid].loc = loc
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
		a = True
		while True:
			time.sleep(.02)
			self.disp.render()
			if len(self.conn.Q):
				self.conn.parse(self.conn.Q.popleft())
			inp.retrieve()
			new = Location(loc=self.player.loc)
			if inp.value != ([], []):
				if 'q' in inp.value[0]: 
					sys.exit()
				if 'w' in inp.value[0]: 
					new.y -= 1         
				if 'a' in inp.value[0]:
					new.x -= 1
				if 's' in inp.value[0]:
					new.y += 1
				if 'd' in inp.value[0]:
					new.x += 1
				if new != self.player.loc:
					self.move(new)

				
				a = False

g = Game()
g.startup()