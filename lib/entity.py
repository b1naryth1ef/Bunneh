from lib import Location
from astar import AStar
import sys, os, time

class Entity():
	def __init__(self, eid, name, pos):
		self.id = eid
		self.name = name
		self.pos = pos

class AI(Entity):
	pathfinder = AStar()
	find = pathfinder.findPath
	goal = "PLAYER"

	def tick(self): pass

	def starMove(self):
		if self.goal == "PLAYER":
			p = self.server.getNearestPlayer(self.pos)
			if p:
				self.find(p.pos.getpos(), self.pos.getpos(), self.server.getLevel(self.pos).map)
				q = self.pathfinder.path
				if q and len(q) > 2: #We can move closer yet!
					print '%s >>> %s' % (self.pos, q[1])
					self.pos = Location(data=list(q[1])+[self.pos.l, self.pos.w])
					return True
				else: pass #We're within one!
		return False

class Player(Entity):
	def __init__(self, eid=None, name=None, pos=None, data=None):
		self.id = eid
		self.name = name
		if not isinstance(pos, Location):
			self.pos = Location(data=pos)
		else:
			self.pos = pos
		self.char = "x"
		if data:
			self.load(data)

	def dump(self):
		return {
			'id':self.id,
			'name':self.name,
			'pos':self.pos.dump(),
			'char':self.char
		}

	def load(self, obj):
		if obj.get('pos'):
			obj['pos'] = Location(data=obj['pos'])
		self.__dict__.update(obj)

class MobHolder(Entity): #Used client side
	def __init__(self, eid=None, name=None, pos=None, char="#", data=None):
		self.id = eid
		self.name = name
		self.pos = pos
		self.char = char

		if data:
			self.load(data)

	def load(self, data):
		self.id = data['id']
		self.name = data['name']
		self.pos = Location(data=data['pos'])
		self.char = data['char']

class LoveBunny(AI): #A bunny that likes players | serverside
	def __init__(self, eid=None, name="Lovey", pos=None, server=None):
		self.id = eid
		self.name = name
		self.pos = pos
		self.server = server
		self.type = "LOVE_BUNNY"
		self.char = "."

		self.lastMove = 0
		self.moveTime = .3

	def tick(self):
		if time.time()-self.lastMove >= self.moveTime:
			self.lastMove = time.time()
			q = self.starMove()
			if q:
				self.server.globalSend({'action':'ENT_POS', 'id':self.id, 'loc':self.pos.dump()})

	def dump(self):
		return {
			'id':self.id,
			'name':self.name,
			'pos':self.pos.dump(),
			'char':self.char,
		}

mob_types = {
	'LOVE_BUNNY':LoveBunny,
}
