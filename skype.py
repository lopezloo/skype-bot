# -*- coding: utf-8 -*-
import Skype4Py

g_debug = True

g_chats = {
          "test" :  "#lopezloo/$f6d1b455dba8824",
          "mta"  :  "#divx92/$18d4d85908c14588",
          "tr"   :  "#lopezloo/$1df2f3dc7ef04417"
}

def connectToSkype():
    global g_skype
    print("connectToSkype")
    try:
        g_skype = Skype4Py.Skype()
        g_skype.Attach()
    except Exception:
        print("Failed to attach to skype.")
        quit()

def sendMessageToChat ( theChat, message ):
    if g_debug:
        theChat = g_chats["test"]

    if type(theChat) is Skype4Py.chat.Chat:
        # skype chat object
        return theChat.SendMessage( message )
    else:
        # chat name
        for chat in g_skype.Chats:
            if chat.Name == theChat:
                return chat.SendMessage( message )
