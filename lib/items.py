
class Item():
    id = 0
    name = "Base Item"

    hasDura = False

    isWeapon = False
    isTool = False
    isEdible = False

    durability = [50, 50]

    def __init__(self):
        self.setup()

    def setup(self): pass

    def actionFight(self): pass
    def actionUse(self): pass
    def actionEat(self): pass

class Inventory():
    name = "Base Inventory"
    slots = 10
    id = 0

    def __init__(self):
        self._inv = {}
        for i in range(1, self.slots+1):
            self._inv[i] = None
        self.setup()

    def dump(self):
        r = {
            'id':self.id,
            'slots':{}
        }
        for i in self._inv.values():
            r['slots'][i] = i.dump()
        return r

    def load(self):
        for i in r['slots']:
            self._inv[i] = loadItem(r['slots'][i])

    def setup(self): pass

    def getEmptySlots(self):
        return [i for i in self._inv if self._inv[i] == None]

    def getFilledSlots(self):
        return [i for i in self._inv if self._inv[i] != None]

    def addItem(self, obj):
        q = self.getEmptySlots()
        if len(q) and isinstance(obj, Item):
            self._inv[q[0]] = obj 

    def movItem(self, froms, tos):
        q = self.getEmptySlots()
        if froms not in q and tos in q:
            self._inv[tos] = self._inv[froms]
            self.delItem(froms)

    def getItem(self, slot):
        if self._inv[slot] != None:
            return self._inv[slot]

    def delItem(self, slot):
        del self._inv[slot]

class BasicBackPack(Inventory):
    name = "Basic backpack"
    slots = 10
    id = 1

class Stick(Item):
    id = 1
    name = "Stick"

def loadItem(data):
    return ITEMS[data['id']](data)

ITEMS = {
    1:Stick,
}

test_inventory = BasicBackPack()
test_inventory.addItem(Stick())
test_inventory.addItem(Stick())
test_inventory.addItem(Stick())