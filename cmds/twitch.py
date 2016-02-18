# -*- coding: utf-8 -*-
import utils, skype
from commands import Command

def cmd_twitch ( chat, nick ):
    data = utils.getJSON ( "https://api.twitch.tv/kraken/streams/" + nick )
    if data is None:
        return

    if "error" in data:
        skype.sendMessageToChat( chat, "Nie ma takiego kanału.")
        return

    if data["stream"] is not None:
        nick = data["stream"]["channel"]["display_name"]
        game = data["stream"]["game"]
        status = data["stream"]["channel"]["status"]
        viewers = str(data["stream"]["viewers"])
        fps = str( int( round(data["stream"]["average_fps"]) ) )

        if game:
            skype.sendMessageToChat( chat, nick + " streamuje " + game + " (" + status + ", " + viewers + " widzów, " + fps + " FPS)\nhttps://twitch.tv/" + nick )
        else:
            skype.sendMessageToChat( chat, nick + " prowadzi stream (" + status + ", " + viewers + " widzów, " + fps + " FPS)\nhttps://twitch.tv/" + nick )
    else:
        skype.sendMessageToChat( chat, nick + " obecnie nic nie streamuje!" )
    return
Command ( "!twitch", cmd_twitch )

def cmd_twitchTop ( chat, category = "" ):
    if category != "":
        data = utils.getJSON( "https://api.twitch.tv/kraken/search/games?type=suggest&live=1&limit=1&q=" + category )
        if data is None:
            return
        if len(data["games"]) == 0:
            skype.sendMessageToChat( chat, "Nie ma takiej kategorii.")
            return
        category = data["games"][0]["name"]

    data = utils.getJSON( "https://api.twitch.tv/kraken/streams?limit=3&game=" + category )
    if data is None:
        return

    if len(data["streams"]) == 0:
        skype.sendMessageToChat( chat, "Brak streamów w kategorii " + category )
        return

    txt = ""
    for k, stream in enumerate( data["streams"] ):
        nick = stream["channel"]["display_name"]
        status = stream["channel"]["status"]
        viewers = str(stream["viewers"])
        fps = str( int( round(stream["average_fps"]) ) )
        if len(arg) > 0:
            txt = txt + "\n" + str(k + 1) + ". " + nick + " (" + status + ", " + viewers + " widzów, " + fps + " FPS) https://twitch.tv/" + nick
        else:
            game = stream["game"]
            txt = txt + "\n" + str(k + 1) + ". " + nick + " (" + game + ", " + status + ", " + viewers + " widzów, " + fps + " FPS) https://twitch.tv/" + nick

    if len(category) > 0:
        skype.sendMessageToChat( chat, "Top 3 streamów z kategorii " + category + ":" + txt)
    else:
        skype.sendMessageToChat( chat, "Top 3 streamów:" + txt)
    return
Command( "!twitchtop", cmd_twitchTop )
