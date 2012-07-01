import json

class Var():
	def __init__(self, name, value, writeable=True, varlist=None):
		self.name = name
		self.value = value

		if varlist: varlist.add(self)

		self.canWrite = writeable

	def __str__(self):
		return self.value

	def __len__(self):
		return len(self.value)

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
	def __init__(self, x=0, y=0, w=0, loc=None, data=None):
		self.x = x
		self.y = y
		self.w = w
		self.pos = property(self._getpos, self._setpos)
		if data:
			if type(data) is str: self.loads(data)
			elif type(data) is dict: self.load(data)
			elif type(data) is list: 
				self.x, self.y, self.w = data
		if loc and isinstance(loc, Location):
			self.x = loc.x
			self.y = loc.y
			self.w = loc.w

	def dump(self): return {'x':self.x, 'y':self.y, 'w':self.w}
	def dumps(self): return json.dumps(self.dump())
	def load(self, d): self.__dict__.update(d)
	def loads(self, d): self.load(json.loads(d))

	def _getpos(self):
		return [self.x, self.y]

	def _setpos(self, val):
		self.x = val[0]
		self.y = val[1]

	def __eq__(self, obj):
		if isinstance(obj, Location) and obj.w == self.w:
			x, y = obj.x, obj.y
		elif isinstance(obj, list) or isinstance(obj, tuple):
			x, y = obj
		elif isinstance(obj, dict):
			x, y = obj['x'], obj['y']
		else: return False

		if self.pos == [x, y]:
			return True
		else:
			return False

	def __repr__(self):
		return "<Location x=%s, y=%s, w=%s>" % (self.x, self.y, self.w)

class World():
	def __init__(self, wid, level):
		self.id = wid
		self.start = Location(data=level.spawnpos+[wid])
		self.level = level
		self.ents = {}

	def addEnt(self, ent=None):
		eid = max(self.ents.keys())+1
		self.ents[eid] = ent
		return eid

def checkMove(player, loc, lvl):
	if -1 <= player.loc.x-loc.x <= 1 and -1 <= player.loc.y-loc.y <= 1 and lvl.checkMove(loc):
		return True
	return False

