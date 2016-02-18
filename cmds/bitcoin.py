# -*- coding: utf-8 -*-
import utils, skype, datetime
from commands import Command

def cmd_bitcoin ( chat ):
    data = utils.getJSON( 'https://www.bitmarket.pl/json/BTCPLN/ticker.json' )
    if data is None:
        return
    txt = "1 BTC = " + str(data["last"]) + " PLN"            
    data = utils.getJSON( 'https://www.bitmarket.pl/json/LTCPLN/ticker.json' )
    if data is None:
        return
    skype.sendMessageToChat( chat, txt + "\n1 LTC = " + str(data["last"]) + " PLN" )

Command ( "!btc", cmd_bitcoin )
Command ( "!ltc", cmd_bitcoin )