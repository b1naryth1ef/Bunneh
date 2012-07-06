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


def addUser(obj):
	u = User(name=obj.name, pos=obj.loc, hashkey=str(random.randrange(10e14, 10e15)))
	u.save()
	return u

def getUser(obj, hashk):
	q = [i for i in User.select().where(name=obj.name)]
	if len(q):
		if q[0].hashkey == hashk:
			return q[0]
	else:
		return addUser(obj)
	return None

User.create_table(True)