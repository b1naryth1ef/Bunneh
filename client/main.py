from clib.pygcurse import PygcurseWindow
from clib.inputlib import KeyboardInput
from clib.const import *
from lib.lib import World, Location, checkMove, Var, Varlist
from lib.mapper import test
from lib.entity import Player
from connection import Connection
from display import Display
from commands import commands

import pygame, thread, random
import sys, os, time

win = PygcurseWindow(80, 60, fullscreen=False, fontsize=14)
conn = Connection()
inp = KeyboardInput()

DEV_MODE = True

pygame.display.set_caption('Bunneh')

class Game():
	def __init__(self):
		self.win = win
		self.update = False
		self.conn = conn
		self.disp = Display(win, self)
		self.inp = inp
		self.running = False
		self.worlds = {
			1:World(1, test)
		}

		self.varlist = Varlist()
		
		self.msg = []
		self.players = {}

		self.get = self.varlist.getval

	def quit(self):
		self.conn.disconnect()
		sys.exit()

	def setup(self):
		Var('console_prefix', '>>', varlist=self.varlist)
		Var('chat_keeptime', 3, varlist=self.varlist)

	def getCurrentWorld(self):
		return self.worlds[self.player.pos.w]

	def move(self, new):
		if checkMove(self.player, new, self.getCurrentWorld().level):
			self.player.pos = new
			self.conn.write({'action':'ACTION', 'type':'MOVE', 'pos':new.dump()})  
			self.disp.updaterender = True

	def updatePos(self, cid, loc):
		self.players[cid].pos = loc
		self.disp.updaterender = True

	def addMsg(self, msg):
		self.msg.append({'content':msg, 'type':'con', 'time':None})
		self.disp.updaterender = True

	def addChat(self, msg):
		self.msg.append({'content':msg[1], 'type':'msg', 'id':msg[0], 'time':None})
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

	def startScreen(self):
		g = self.disp.getCenterPos('Server IP: ')
		ip = self.win.input("Server IP: ", g[0], g[1], fgcolor=BLUE)
		g = self.disp.getCenterPos('Username: ')
		name = self.win.input('Username: ', g[0], g[1], fgcolor=BLUE)
		self.conn.connect(game=self, ip=ip, name=name)

	def startLoop(self):
		self.setup()
		thread.start_new_thread(self.conn.loop, ())
		self.running = True
		self.conn.write({'action':'INFO'})
		while True:
			time.sleep(.03)
			self.disp.render()
			if len(self.conn.Q):
				self.conn.parse(self.conn.Q.popleft())
			inp.retrieve()
			new = Location(loc=self.player.pos)
			if inp.value != ([], []):
				if 'q' in inp.value[0]: self.quit()
				if 'w' in inp.value[0]: new.y -= 1         
				if 'a' in inp.value[0]: new.x -= 1
				if 's' in inp.value[0]: new.y += 1
				if 'd' in inp.value[0]: new.x += 1
				if 't' in inp.value[0]:
					txt = self.win.input("Talk: ", 0, self.disp.offset, fgcolor=BLUE)
					if txt: self.conn.write({'action':'ACTION', 'type':'MSG', 'data':txt})
					self.update = True
				if 'c' in inp.value[0]:
					txt = self.win.input("Console: ", 0, self.disp.offset, fgcolor=BLUE)
					if txt:
						txt = txt.split(' ')
						if commands.get(txt[0]): 
							commands.get(txt[0])(txt, self)
						else: self.conn.write({'action':'ACTION', 'type':'CMD', 'data':' '.join(txt)})
				if new != self.player.pos: self.move(new)
			if self.disp.checkChat():
				self.update = True
			if self.update:
				self.disp.updaterender = True
				self.update = False

g = Game()
g.startScreen()