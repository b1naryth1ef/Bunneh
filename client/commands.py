commands = {}

def cmd(c):
    def deco(func):
        if c not in commands.keys():
            commands[c] = func
            return func
        raise Exception('Duplicate hook!')
    return deco


@cmd('echo')
def echo_cmd(c, g):
	g.addMsg(' '.join(c[1:]))

@cmd('set')
def echo_cmd(c, g):
	if len(c) >= 3:
		if g.varlist.has(c[1]):
			if g.varlist.get(c[1]).canWrite:
				if len(c) == 3 and c[2].isdigit(): v = int(c[2])
				else: v = ' '.join(c[2:])
				print v
				g.varlist.get(c[1]).value = v
				g.addMsg('Var %s set to %s' % (c[1], v))
			else:
				g.addMsg('Var %s is unwriteable!' % c[1])
		else:
			g.addMsg('No such var %s' % c[1])
