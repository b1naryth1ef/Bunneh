from lib import Location

class Entity():
	def __init__(self, eid, name, loc):
		self.eid = eid
		self.name = name
		self.pos = loc

class Player(Entity):
	def __init__(self, name=None, id=None, loc=None, data=None):
		self.id = id
		self.name = name
		if not isinstance(loc, Location):
			self.loc = Location(data=loc)
		else:
			self.loc = loc
		self.char = "x"
		if data:
			self.load(data)

	def dump(self):
		return {
			'id':self.id,
			'name':self.name,
			'loc':self.loc.dump(),
			'char':self.char
		}

	def load(self, obj):
		if obj.get('loc'):
			obj['loc'] = Location(data=obj['loc'])
		self.__dict__.update(obj)