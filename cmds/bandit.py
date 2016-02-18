# -*- coding: utf-8 -*-
import utils, skype, random, time
from commands import Command

# todo: fix size args
def cmd_bandit ( chat, size_x, size_y ):
    size_x = int(size_x)
    if size_x is None:
        size_x = 3
    size_x = int(size_y)
    if size_y is None:
        size_y = 3

    if size_x < 1:
        size_x = 1
    elif size_x > 8:
        size_x = 8
    if size_y < 1:
        size_y = 1
    elif size_y > 5:
        size_y = 5

    #icons = [ ':)', ':(', ':D', '(cool)', ';)', ':o', '(sweat)', ':|', ':*',
    #':P', '(yn)', '(blush)', ':^)', '(snooze)', '|(', '(inlove)', '(yawn)',
    #'(puke)', '(doh)', '(wasntme)', '(facepalm)', ':S', '(mm)', '8-|',
    #':x', '(wave)', '(devil)', '(envy)', '(makeup)', '(moustache)',
    #'(giggle)', '(clap)', '(think)', '(happy)', '(smirk)',
    #'(nod)', '(shake)', '(emo)', '(tmi)', '(rock)', '(swear)',
    #'(punch)', '(talk)', '(call)',
    #'(wtf)', '(donttalk)' ]

    icons = [ '(heidy)', '(hug)', '(dog)', '(sun)', '(coffee)', '(^)', '(cash)', '(gift)',
    '(tandoori)', '(cheese)', '(d)', '(bell)', '(cat)', '(~)', '(heart)', '(mooning)' ]
    
    txt = ""
    lines = []
    for i in range( 0, size_y ):
        line = []
        for j in range( 0, size_x ):
            line.insert( j, random.choice(icons) )
            txt = txt + line[j] + " "
        lines.insert( i, line )
        txt = txt + "\n"

    message = skype.sendMessageToChat( chat, txt )

    for o in range(1, 21):
        time.sleep( 0.2 )
        txt = ""
        for i in reversed(range( 0, size_y )):
            for j in reversed(range( 0, size_x )):
                if i > 0:
                    lines[i][j] = lines[i-1][j]
                else: # 2
                    lines[i][j] = random.choice(icons)
                txt = txt + lines[i][j] + " "
            txt = txt + "\n"
        message.Body = txt

Command ( "!bandit", cmd_bandit )