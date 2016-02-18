# -*- coding: utf-8 -*-
import utils, skype, datetime
from commands import Command

def cmd_orct ( chat ):
    data = utils.getJSON( "https://servers.openrct2.website/" )
    if data is None or data["status"] != 200:
        skype.sendMessageToChat( chat, "Master server leży." )
        return

    total_players = 0
    total_slots = 0
    txt = "Serwery OpenRCT2:\n"
    for server in data["servers"]:
        if server["requiresPassword"]:
            txt = txt + " 🔒 "
        else:
            txt = txt + "     "
        txt = txt + server["name"] + " " + str(server["players"]) + "/" + str(server["maxPlayers"]) + " (" + server["ip"]["v4"][0] + ":" + str(server["port"]) + ")\n"
        total_players = total_players + server["players"]
        total_slots = total_slots + server["maxPlayers"]
    skype.sendMessageToChat( chat, txt + "Łącznie " + str(total_players) + "/" + str(total_slots) + " graczy." )

Command ( "!rct", cmd_orct )
Command ( "!rct2", cmd_orct )
Command ( "!orct", cmd_orct )
Command ( "!orct2", cmd_orct )
