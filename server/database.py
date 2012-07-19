from peewee import *
import sys, os, time
from lib.lib import Location
import random

db = SqliteDatabase("bunneh.db")

class User(Model):
	class Meta:
		database = db
	name = CharField()
	pos = CharField()
	hashkey = CharField()
	ip = CharField()
	data = CharField()
	banned = BooleanField()

def addUser(obj):
	print 'Adding user!'
	u = User(name=obj.player.name, 
		pos=obj.player.pos.dumps(), 
		ip=obj.addr.host,
		hashkey=str(random.randrange(10e14, 10e15)))
	u.save()
	return u

def isBanned(obj):
	q = [i for i in User.select().where(ip=obj.addr.host) if i.banned is True]
	if len(q): return True
	return False

def getUser(obj, hashk):
	q = [i for i in User.select().where(name=obj.player.name)]
	if len(q):
		if q[0].hashkey == hashk:
			return q[0]
		else:
			return 'Invalid haskey! Someone with a username may already exist!'
	else:
		if not isBanned(obj):
			return addUser(obj)
		else:
			return 'Banned!'

def getUserByID(uid):
	return [i for i in User.select().where(id=uid)][0]


User.create_table(True)