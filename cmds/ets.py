# -*- coding: utf-8 -*-
import utils, skype, datetime
from commands import Command

def cmd_ets ( chat ):
    # servers status
    data = utils.getJSON('https://api.ets2mp.com/servers/')
    if data is None:
        return

    if data["error"] != "false":
        return

    txt = "Serwery TruckersMP:"
    total_players = 0
    total_slots = 0
    for server in data["response"]:
        txt = txt + "\n" + server["game"] + " " + server["name"]
        if server["online"]:
            txt = txt + " (" + str(server["players"]) + "/" + str(server["maxplayers"]) + ")"
            total_players = total_players + server["players"]
            total_slots = total_slots + server["maxplayers"]
        else:
            txt = txt + " (offline)"
    txt = txt + "\nŁącznie " + str(total_players) + "/" + str(total_slots) + " graczy."

    # game time
    data = utils.getJSON( 'https://api.ets2mp.com/game_time/' )
    if data is not None:
        if data["error"]:
            return

        gameTime = datetime.datetime(2015, 10, 25) + datetime.timedelta( minutes = data["game_time"] );
        txt = txt + "\nCzas w grze: " + gameTime.strftime('%H:%M')

    # song at TruckersFM
    data = utils.getURL( 'http://truckers.fm/' )
    if data is not None:
        song_start = data.find( '<span id="currently_playing"> <span id="song"><span class="song-details">' ) + 73
        if song_start != 72:
            song_end = data.find('</span>', song_start)
            txt = txt + "\nTruckersFM: " + data [ song_start : song_end ]

    skype.sendMessageToChat ( chat, txt )

Command ( "!ets", cmd_ets )
Command ( "!ats", cmd_ets )
Command ( "!truckersmp", cmd_ets )
