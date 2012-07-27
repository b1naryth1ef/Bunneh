from clib.const import *
from lib.items import test_inventory as inv
import sys, os, time

class BaseDisplay():
    def __init__(self, disp):
        self.d = disp
        self.game = disp.game

    def render(self): pass

class GameDisplay(BaseDisplay):
    def render(self):
        self.d.reset()
        self.renderMap()
        self.renderChat()
        return True

    def renderMap(self):
        for x, row in enumerate(self.game.getCurrentLevel().map.getRender()):
            self.d.displayText(row, 0, x, fgcolor=(255,   0,   0), bgcolor=(  0,   0,   0))
            self.d.offset += 1
        if not self.game.var.get('hide_ents'):
            for ent in self.game.getCurrentLevel().ents.values():
                self.d.displayText(ent.char, ent.pos.x, ent.pos.y, fgcolor=ORANGE)
        for plyr in self.game.players.values():
            if self.game.var.get('hide_players') and not plyr == self.game.player:
                continue
            pos = plyr.pos
            self.d.displayText(plyr.char, pos.x, pos.y, fgcolor=(0,255,0))

    def renderChat(self):
        self.d.offset += 1
        self.game.checkChat()
        for msg in self.game.msg:
            if msg['type'] is 'msg':
                name = '%s: ' % self.game.players[msg['id']].name
                self.d.displayText(name, 0, self.offset, fgcolor=RED)
                self.d.displayText(msg['content'], len(name), self.d.offset, fgcolor=BLUE)
            elif msg['type'] is 'con':
                self.d.displayText(str(self.game.var.get('console_prefix')), 0, self.d.offset, fgcolor=BLUE)
                self.d.displayText(msg['content'], len(self.game.var.get('console_prefix'))+1, self.d.offset, fgcolor=RED)
            self.offset += 1

class InventoryDisplay(BaseDisplay):
    def render(self):
        self.d.reset()
        self.renderList()
        return True

    def renderList(self):
        setb = 1
        for item in inv.getFilledSlots():
            self.d.offset += 1
            btxt = "#%s" % item
            self.d.displayText(btxt, setb, self.d.offset, fgcolor=BLUE)
            self.d.displayText(':', setb+len(btxt)+1, self.d.offset, fgcolor=ORANGE)
            self.d.displayText(inv.getItem(item).name, setb+len(btxt)+2, self.d.offset, fgcolor=RED)

class Display(object):
    def __init__(self, win, game):
        self.win = win
        self.game = game
        self.updaterender = True
        self.offset = 0
        self.chat_times = {}

        self.displaymodes = [GameDisplay(self), InventoryDisplay(self)]
        self.displaymode = 0

    def blank(self): self.win.setscreencolors(clear=True)
    def clear(self): 
        self.blank()
        self.win.update()
    def reset(self):
        self.blank()
        self.offset = 0

    def render(self):
        if self.updaterender and self.displaymodes[self.displaymode].render():
            self.updaterender = False
            self.win.update()
        return

    def displayInfo(self, s=50):
        self.displayText('-'*80, 0, s)
        p = self.game.getPlayer()

        #Player Name
        s+=1
        self.displayText('Name: ', 0, s, fgcolor=BLUE)
        self.displayText(p.name, 6, s, fgcolor=RED)

        #Player health
        s+=1
        self.displayText('Health: [', 0, s, fgcolor=BLUE)
        if p.health[0] > 5: htxt = '%s%s' % ('='*(int(round(p.health[0]))/5), ' '*abs((int(round(p.health[0]))-p.health[1])/5))
        else: htxt = '= '+' '*4
        self.displayText(htxt, 9, s, fgcolor=RED)
        self.displayText(']', 18, s, fgcolor=BLUE)

    def getCenterPos(self, text, inc=False):
        x = (self.win.centerx-len(text)/2)
        y = self.win.centery
        if inc:
            x += self.offset[0]
            y += self.offset[1]
        return (x, y)

    def centerText(self, text, y=0, x=0, **args):
        self.win.putchars(text, (self.win.centerx-len(text)/2)+x, self.win.centery+y, **args)

    def displayText(self, *args, **kwargs):
        self.win.putchars(*args, **kwargs)

    def message(self, message, *args, **kwargs):
        self.blank()
        self.centerText(message, 0, 0, *args, **kwargs)
        self.centerText('[enter]', 1, 0, *args, **kwargs)
        self.win.update()
        self.game.inp.waitFor('enter')
        self.updaterender = True


