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
			self.pos = Location(data=loc)
		else:
			self.pos = loc
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