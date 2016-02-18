# -*- coding: utf-8 -*-
import utils, skype, datetime
from commands import Command

def cmd_steam ( chat ):
    data = utils.getJSON( 'http://store.steampowered.com/api/featured/' )
    if data is None:
        return

    txt = "Polecane:\n"
    for game in data["large_capsules"]:
        price1 = str(game["final_price"])[ : -2 ]
        if price1 == "":
            price1 = "0"
        price2 = str(game["final_price"])[ -2 : ]
        txt = txt + game["name"] + " " + price1 + "." + price2 + "€"
        if game["discounted"] and game["discount_percent"] > 0:
            txt = txt + " [-" + str(game["discount_percent"]) + "%]"
        txt = txt + "\n"
    skype.sendMessageToChat ( chat, txt )

Command ( "!steam", cmd_steam )