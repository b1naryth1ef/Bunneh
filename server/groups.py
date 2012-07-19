class BaseLevel(object):
	canMove = False
	canTalk = False
	canCmd = False
	canKick = False
	canMute = False
	canBan = False
	canChangeVar = False
	canChangeUserVar = False
	canKillServer = False

	talkThrottle = .3
	moveThrottle = .06

class NewbLevel(BaseLevel):
	canMove = True
	canTalk = True
	canCmd = True

class ModLevel(NewbLevel):
	canKick = True
	canMute = True
	canBan = True

class AdminLevel(ModLevel):
	canChangeVar = True
	canChangeUserVar = True
	canKillServer = True

	talkThrottle = 0