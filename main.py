# -*- coding: utf-8 -*-
import sys

import skype
import utils
import notifications
import commands

# Disable calls completly (auto refuse every call). todo reintro this later
#def OnCallStatus ( call, status ):
#    if status == "RINGING":
#        print( call.PartnerHandle.encode('utf-8') + " calls" )
#        try:
#            call.Finish(); # this always throw some strange exception but works
#        except Exception:
#            print('');

#def OnChatMembersChanged ( chat, members ):
#    chat.SendMessage("OnChatMembersChanged")
    #for member in members:
    #    chat.SendMessage(member.Handle)
#g_skype.OnChatMembersChanged = OnChatMembersChanged



print("skype.py")
def main():
    print("skype.py main()")
    reload(sys)  
    sys.setdefaultencoding('utf8')

    skype.connectToSkype()
    utils.loadSettings()
    notifications.initNotifications()
    commands.init()

    #import commands

if __name__ == "__main__":
    main()
