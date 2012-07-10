from lib import Location

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
        self.spawnpos = [1, 1]
        self.bounds = [0, 0]
        self.genHitMap()

    def checkMove(self, pos):
        if isinstance(pos, Location): pos = (pos.x, pos.y)
        else: pos = tuple(pos)
        if 0 < pos[0] < self.bounds[0] and 0 < pos[1] < self.bounds[1]:
            if pos in self.hit.keys():
                return self.hit[tuple(pos)]['empty']
        return False #Expected behaivor: return bool

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
        maxX, maxY = [], []
        for ypos, row in enumerate(self.clean):
            maxY.append(ypos)
            for xpos, char in enumerate(row):
                maxX.append(xpos)
                cpos = (xpos, ypos)
                if char == '#':
                    self.hit[cpos] = {'empty':False, 'draw':True, 'special':[False]}
                elif char == '0':
                    self.hit[cpos] = {'empty':True, 'draw':False, 'special':[True, 'spawn']}
                    self.spawnpos = list(cpos)
                else:
                    self.hit[cpos] = {'empty':True, 'draw':True, 'special':[False]}
        self.bounds = [max(maxX), max(maxY)]
        print 'Bounds:', self.bounds

test = Map(clean, action)