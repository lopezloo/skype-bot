# -*- coding: utf-8 -*-
import inspect
import sys
import json

import skype
import utils

g_commands = []

class Command:
    def __init__ ( self, name, function, description = "" ):
        self.name = name
        self.function = function
        self.description = description
        g_commands.append( self )

        #print("args: " + getArgumentsCount())

    def getArgumentsCount ( self ):
        #return self.function.__code__.co_argcount
        return len( self.getArguments() )

    def getArguments ( self ):
        #return self.function.__code__.co_varnames
        args, _, _, _ = inspect.getargspec( self.function )
        return args

    def callFunction ( self, args ):
        self.function ( *args )

    def process ( self, message, chat ):
        print("getArgumentsCount(): " + str(self.getArgumentsCount()))

        print("Required arguments:")
        for arg in self.getArguments():
            print(arg)

        msgArgs = message.split ( )
        print("Arguments:")

        #msgArgs.remove ( self.name )
        # put chat as first argument instead of cmd name
        msgArgs[0] = chat
        print(msgArgs)
        for arg in msgArgs:
            print(arg)

        if self.getArgumentsCount() == 2 and len(msgArgs) > 1:
            # cmd require only 1 argument, pass all args as only 1
            msgArgs.remove(chat)
            arg = " ".join(msgArgs)
            self.callFunction ( [ chat, arg ] )
        elif len(msgArgs) == self.getArgumentsCount():
            # exact amount of arguments
            self.callFunction( msgArgs )

        elif len(msgArgs) > self.getArgumentsCount():
            # too much arguments passed, cut it
            for i in range( self.getArgumentsCount(), len(msgArgs) ):
                msgArgs.pop ()
            self.callFunction( msgArgs )
        else:
            # too less arguments, output command schema (without first chat argument)
            txt = "Użycie: " + self.name
            args = self.getArguments()
            for i in range(1, len( args )):
                txt = txt + " [" + args[i] + "]"
            if self.description != "":
                txt = txt + " (" + self.description + ")"
            skype.sendMessageToChat( chat, txt )

def OnMessageStatus ( message, status ):
    print("OnMessageStatus")
    if status == 'RECEIVED':
        for command in g_commands:
            #if message.Body.find(command.name) == 0:
            if message.Body.split()[0] == command.name:
                command.process( message.Body, message.Chat )
                return

        # other stuff
        if message.Body.find('v=') >= 0 or message.Body.find('youtu.be/') >= 0:
            link_start = message.Body.find('youtu.be/') + 9
            if link_start - 9 == -1:
                link_start = message.Body.find('v=') + 2

            link_end = message.Body.find('&', link_start)
            if link_end == -1:
                link_end = message.Body.find(' ', link_start)
                if link_end == -1:
                    link_end = len( message.Body )

            vidID = message.Body [ link_start : link_end ]
            data = utils.getJSON( "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=AIzaSyDViQNqCB7CxTiqS5YiBogXVBykLUtrUmY&id=" + vidID )
            if data is None:
                return
            if len(data["items"]) > 0:
                title = data["items"][0]["snippet"]["title"]
                skype.sendMessageToChat( message.Chat, 'YT: ' + title)
            return

        if message.Body.find('lenny') != -1:
            skype.sendMessageToChat( message.Chat, "( ͡° ͜ʖ ͡°)" )
        return

        if message.Body.find('community.mtasa.com/index.php?p=resources&s=details&id=') >= 0:
            link_start = message.Body.find( 'community.mtasa.com/index.php?set_lang=eng&p=resources&s=details&id=' ) + 55
            link_end = message.Body.find( ' ', link_start )
            if link_end == -1:
                link_end = len(message.Body)

            if link_start >= 0:
                source = utils.getURL( "http://community.mtasa.com/index.php?p=resources&s=details&id=" + message.Body[ link_start : link_end ] )
                if source is None:
                    return

                title_start = source.find( '">rss</a></span>' ) + 16
                title_end = source.find( '</h2>', title_start ) - 3
                title = source [ title_start : title_end ]

                if title_start - 16 == -1:
                    return

                author_start = source.find( '<tr><th>Author:</th><td><a href="?p=profile&amp;id=' ) + 51
                author_start = source.find( '">', author_start ) + 2
                author_end = source.find( '</a>', author_start )
                author = source [ author_start : author_end ]

                downloads_start = source.find( '<tr><th>Downloads:</th><td>' ) + 27
                downloads_end = source.find( '</td>', downloads_start )
                downloads = source [ downloads_start : downloads_end ]

                skype.sendMessageToChat( message.Chat, 'Community: ' + title + " @ " + author + " (" + downloads + " pobrań)" )
            return

        if message.Body.find('store.steampowered.com/app/') >= 0:
            link_start = message.Body.find('store.steampowered.com/app/') + 27
            link_end1 = message.Body.find('/', link_start)
            link_end2 = message.Body.find(' ', link_start)

            link_end = link_end1
            if (link_end2 < link_end and link_end2 != -1) or link_end == -1:
                link_end = link_end2

            if link_end == -1:
                link_end = len(message.Body)

            appID = message.Body [ link_start : link_end ]
            data = utils.getJSON( 'http://store.steampowered.com/api/appdetails?appids=' + appID )

            if data is None:
                return

            if not data[appID]["success"]:
                return

            data = data[appID]["data"]
            txt = "Steam: " + data["name"]
            if data["is_free"]:
                txt = txt + " (darmowe)"
            else:
                price1 = str(data["price_overview"]["final"])[ : -2 ]
                if price1 == "":
                    price1 = "0"
                price2 = str(data["price_overview"]["final"])[ -2 : ]

                if data["price_overview"]["currency"] == "EUR":
                    currency = "€"
                else:
                    currency = "$"

                txt = txt + " " + price1 + "." + price2 + currency
                if data["price_overview"]["discount_percent"] > 0:
                    txt = txt + " [-" + str(data["price_overview"]["discount_percent"]) + "%]"
            message.Chat.SendMessage ( txt )
            return

def init():
    print("commands.init()")
    skype.g_skype.OnMessageStatus = OnMessageStatus

    # Import commands from /cmds/
    sys.path.append("cmds")
    import twitch
    import hitbox
    import mtawiki
    #import idsearch # todo fix json file path
    import bandit
    import gtao
    import bitcoin
    import steam

    import ets
    import orct


# SOME COMMANDS \/
def cmd_help ( chat ):
    txt = "!twitch [nick]\n!twitchtop [opcjonalnie kategoria] - top streamy z danej kategorii\n!hitbox [nick]\n!topic\n\
!lines - ilosć linii w kodzie\n!id [pojazd/kategoria]\n!steam\n!ets - status serwerów TruckersMP\n!bandit\n\
!btc - przelicznik btc/pln i ltc/pln\n!gtao - status serwerów gtao\n!rct - status serwerów OpenRCT2"
    if chat.Name == skype.g_chats["mta"]:
        txt = txt + "\n!w(iki) [tytuł]"
    skype.sendMessageToChat ( chat, txt )
Command ( "!help", cmd_help )
Command ( "!help", cmd_help )
Command ( "!pomoc", cmd_help )
Command ( "!cmd", cmd_help )
Command ( "!cmds", cmd_help )

def cmd_topic ( chat ):
    skype.sendMessageToChat ( "Aktualny temat: " + chat.Topic )
Command ( "!topic", cmd_topic )
Command ( "!temat", cmd_topic )

def cmd_cmdsystem ( chat ):
    skype.sendMessageToChat ( chat, "Zdefiniownych komend: " + str( len(g_commands) ) )
Command ( "!cmdsystem", cmd_cmdsystem )