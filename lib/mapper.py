clean = [
"#######################################",
"#0###                                 #",
"# ### ######                   ##     #",
"# ### #                        ##     #",
"# ### #           ###          ##     #",
"# ### #           ###                 #",
"# ### #                               #",
"# ### #     ####            ##        #",
"# ### #      ###            ##        #",
"# ### #       ##            ##        #",
"#     #                               #",
"#######################################",
]

action = {}

class Map(object):
    def __init__(self, clean, actions):
        self.clean = clean
        self.rower = []
        self.hit = {}
        self.actions = actions
        self.special = {}
        self.spawnpos = [0, 0]
        self.genHitMap()

    def getHit(self, pos):
        return self.hit[tuple(pos)]['empty']

    def getRender(self):
        r = []
        for ypos, row in enumerate(self.clean):
            z = []
            for xpos, char in enumerate(row):
                if self.hit[(xpos, ypos)]['draw']:
                    z.append(char)
                else:
                    z.append(' ')
            r.append(''.join(z))
        return r

    def genHitMap(self):
        for ypos, row in enumerate(self.clean):
            for xpos, char in enumerate(row):
                cpos = (xpos, ypos)
                if char == '#':
                    self.hit[cpos] = {'empty':False, 'draw':True, 'special':[False]}
                elif char == '0':
                    self.hit[cpos] = {'empty':True, 'draw':False, 'special':[True, 'spawn']}
                    self.spawnpos = list(cpos)
                else:
                    self.hit[cpos] = {'empty':True, 'draw':True, 'special':[False]}
        

test = Map(clean, action)