import sys, os, time

commands = {}

def cmd(c):
    def deco(func):
        if c not in commands.keys():
            commands[c] = func
            return func
        raise Exception('Duplicate command!')
    return deco

@cmd('echo')
def echo_cmd(c, g):
	if c[1].startswith('$'):
		if g.varlist.has(c[1][1:]):
			g.addMsg('%s: %s' % (c[1][1:], g.varlist.get(c[1][1:]).value))
	else:
		g.addMsg(' '.join(c[1:]))

@cmd('set')
def echo_cmd(c, g):
	if len(c) >= 3:
		if c[1].startswith('$'): c[1] = c[1][1:]
		if g.varlist.has(c[1]):
			if g.varlist.get(c[1]).canWrite:
				if len(c) == 3 and c[2].isdigit(): v = int(c[2])
				else: v = ' '.join(c[2:])
				g.varlist.get(c[1]).value = v
				g.addMsg('Var %s set to %s' % (c[1], v))
			else:
				g.addMsg('Var %s is unwriteable!' % c[1])
		else:
			g.addMsg('No such var %s' % c[1])

@cmd('quit')
def quit_cmd(c, g):
	g.quit()

@cmd('ping')
def ping_cmd(c, g):
	def resp(packet):
		rt = st-packet['data']
		g.addMsg('Ping: %s' % rt)
		del g.conn.actions['PONG']
	st = time.time()
	g.conn.actions['PONG'] = resp
	g.conn.write({'action':'PING'})
