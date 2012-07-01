from clib.const import *
import sys, os, time

class Display(object):
    def __init__(self, win, game):
        self.win = win
        self.game = game
        self.updaterender = True
        self.offset = 0
        self.chat_times = {}

    def clear(self):
        self.win.setscreencolors(clear=True)
        self.win.update()

    def render(self):
        if self.updaterender:
            self.offset = 0
            self.win.setscreencolors(clear=True)
            self.renderMap()
            self.renderChat()
            #self.displayInfo()
            self.updaterender = False
            self.win.update()
        return

    def renderMap(self):
        for x, row in enumerate(self.game.worlds[self.game.player.loc.w].level.getRender()):
            self.displayText(row, 0, x, fgcolor=(255,   0,   0), bgcolor=(  0,   0,   0))
            self.offset += 1
        for plyr in self.game.players.values():
            pos = plyr.loc
            self.displayText(plyr.char, pos.x, pos.y, fgcolor=(0,255,0))

    def renderChat(self):
        self.offset += 1
        if len(self.game.chat) > 8:
            self.game.chat.pop(0)
            del self.chat_times[0]
        for index, item in enumerate(self.game.chat):
            if index in self.chat_times:
                if time.time()-self.chat_times[index] >= 3:
                    del self.chat_times[index]
                    self.game.chat.pop(index)  
            else:
                self.chat_times[index] = time.time()
            name = '%s: ' % self.game.players[item[0]].name.title()
            self.displayText(name, 0, self.offset, fgcolor=RED)
            self.displayText(item[1], len(name), self.offset, fgcolor=BLUE)
            self.offset += 1


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

    def centerText(self, text, y=0, x=0, **args):
        self.win.putchars(text, (self.win.centerx-len(text)/2)+x, self.win.centery+y, **args)

    def displayText(self, *args, **kwargs):
        self.win.putchars(*args, **kwargs)

    def title(self):
        self.centerText('INVISIBITCH - The Game', fgcolor=RED)
        self.centerText('By B1naryTh1ef', y=2, fgcolor=RED)
        self.centerText('press [a]', y=5, fgcolor=GREEN)
        self.win.update()

    def message(self, message, *args, **kwargs):
        self.win.setscreencolors(clear=True)
        self.centerText(message, 0, 0, *args, **kwargs)
        self.centerText('[enter]', 1, 0, *args, **kwargs)
        self.win.update()
        self.game.inp.waitFor('enter')
        self.updaterender = True

    def invScreen(self): pass
