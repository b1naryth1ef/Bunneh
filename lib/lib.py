import json, zlib
from mapper import Map

class Var():
	def __init__(self, name, value, writeable=True, varlist=None):
		self.name = name
		self.value = value

		if varlist: varlist.add(self)

		self.canWrite = writeable

	def __str__(self):
		return str(self.value)

	def __int__(self):
		return int(self.value)

	def __nonzero__(self):
		return bool(self.value)

	#def __len__(self):
	#	return len(self.value)

class Varlist():
	def __init__(self):
		self._vl = {}

	def add(self, obj):
		self._vl[obj.name] = obj

	def get(self, name):
		if name in self._vl.keys():
			return self._vl[name]

	def getval(self, name):
		return self.get(name).value

	def has(self, name):
		return name in self._vl.keys()

	def __delitem__(self, item):
		del self._vl[item]

class Location():
	def __init__(self, x=0, y=0, l=0, w=0, loc=None, data=None):
		self.x = x 
		self.y = y
		self.l = l #level
		self.w = w #world
		self.pos = property(self._getpos, self._setpos)

		if data:
			if type(data) is str: self.loads(data)
			elif type(data) is dict: self.load(data)
			elif type(data) is list: 
				self.x, self.y, self.l, self.w  = data
		if loc and isinstance(loc, Location):
			self.x = loc.x
			self.y = loc.y
			self.l = loc.l
			self.w = loc.w

	def dump(self): return {'x':self.x, 'y':self.y, 'l':self.l, 'w':self.w}
	def dumps(self): return json.dumps(self.dump())

	def load(self, d):
		self.__dict__.update(d)
		return self

	def loads(self, d): 
		self.load(json.loads(d))
		return self

	def _getpos(self):
		return [self.x, self.y]

	def _setpos(self, val):
		self.x = val[0]
		self.y = val[1]

	def __len__(self):
		return len([self.x, self.y, self.l, self.w])

	def __getitem__(self, item):
		return [self.x, self.y, self.l, self.w][item]

	def __eq__(self, obj):
		if isinstance(obj, Location) and obj.w == self.w:
			x, y = obj.x, obj.y
		elif isinstance(obj, list) or isinstance(obj, tuple):
			x, y = obj
		elif isinstance(obj, dict):
			x, y = obj['x'], obj['y']
		else: return False

		if self.pos == [x, y]: return True
		else: return False

	def __repr__(self):
		return "<Location x=%s, y=%s, l=%s w=%s>" % (self.x, self.y, self.l, self.w)

class Level():
	def __init__(self, lid=1, mapobj=None, data=None):
		self.id = lid
		self.map = mapobj
		self.ents = {} #Dont serialize this for now (until I figure out what its gonna do)

		if data:
			self.load(data)
		elif self.map:
			self.start = self.map.spawnpos+[self.id]
		else:
			self.start = [0, 0]

	def dump(self):
		return {
			'id':self.id,
			'map':self.map.getOrg(),
			'start':self.start
		}

	def load(self, obj):
		self.id = int(obj['id'])
		self.map = Map(*obj['map'])
		self.start = obj['start']

class World():
	def __init__(self, wid=1, levels={}, data=None):
		self.id = wid
		self.levels = levels
		if len(self.levels):
			self.setStart()
		
		if data:
			self.load(data)

	def setStart(self):
		self.start = Location(data=self.levels[1].start+[self.id])

	def dump(self):
		lvls = {}
		for level in self.levels:
			lvls[level] = self.levels[level].dump()

		return {
			'id':self.id,
			'start':self.start.dump(),
			'levels':lvls
		}

	def dumps(self):
		return json.dumps(self.dump())

	def load(self, obj):
		obj = obj
		self.id = int(obj['id'])
		self.start = Location(data=obj['start'])
		for lvl in obj['levels']:
			self.levels[int(lvl)] = Level(data=obj['levels'][lvl])
		self.setStart()

	def loads(self, obj):
		return self.load(json.loads(obj))

	# def addEnt(self, ent=None):
	# 	eid = max(self.ents.keys())+1
	# 	self.ents[eid] = ent
	# 	return eid

def checkMove(player, loc, lvl):
	if -1 <= player.pos.x-loc.x <= 1 and -1 <= player.pos.y-loc.y <= 1 and lvl.checkMove(loc):
		return True
	return False

