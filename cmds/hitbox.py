# -*- coding: utf-8 -*-
import utils, skype
from commands import Command

def cmd_hitbox ( chat, nick ):
    print("cmd_hitbox " + nick)
    data = utils.getJSON ( "https://api.hitbox.tv/media/live/" + nick )
    if data is None:
        # todo: inspect this further
        skype.sendMessageToChat( chat, "api hitboxa jest zjebane" )
        return

    if "error" in data:
        skype.sendMessageToChat ( chat, "Nie ma takiego kanału.")
        return

    nick = data["livestream"][0]["media_display_name"]
    if data["livestream"][0]["media_is_live"] == "0":
        skype.sendMessageToChat ( chat, nick + " obecnie nic nie streamuje!")
        return

    game = data["livestream"][0]["category_name"]
    status = data["livestream"][0]["media_status"]
    viewers = data["livestream"][0]["category_viewers"]
    skype.sendMessageToChat ( chat, nick + " streamuje " + game + " (" + status + ", " + viewers + " widzów)" + "\nhttps://hitbox.tv/" + nick )

Command ( "!hitbox", cmd_hitbox )
