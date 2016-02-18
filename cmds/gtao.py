# -*- coding: utf-8 -*-
import utils, skype, datetime
from commands import Command

def cmd_gtao ( chat ):
    data = utils.getURL( 'https://support.rockstargames.com/hc/en-us/articles/200426246-GTA-Online-Server-Status-Latest-Updates' )
    if data is None:
        skype.sendMessageToChat( chat, "Strona R* leży." )
        return

    pcWarn_start = data.find( '<div id="pcWarn">' ) + 17
    pcWarn_end = data.find( '</div>', pcWarn_start )
    pcWarn = data [ pcWarn_start : pcWarn_end ]

    rsgsUpOrDown_start = data.find( '<div id="rsgsUpOrDown" data-rsgsupordown="', pcWarn_end ) + 42
    rsgsUpOrDown_end = data.find( '"></div>', rsgsUpOrDown_start )
    rsgsUpOrDown = data [ rsgsUpOrDown_start : rsgsUpOrDown_end ]

    pcUpOrDown_start = data.find( '<div id="pcUpOrDown" data-upordown="', rsgsUpOrDown_end ) + 36
    pcUpOrDown_end = data.find( '"></div>', pcUpOrDown_start )
    pcUpOrDown = data [ pcUpOrDown_start : pcUpOrDown_end ]

    txt = "Social Club: " + rsgsUpOrDown + "\nPC: " + pcUpOrDown
    if pcWarn != "" and pcWarn != "no content":
        txt = txt + "\nKomunikat: " + pcWarn
    skype.sendMessageToChat( chat, txt )

Command ( "!gtao", cmd_gtao )
Command ( "!gtaonline", cmd_gtao )
Command ( "!gta", cmd_gtao )