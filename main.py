# -*- coding: utf-8 -*-
import Skype4Py
import urllib, urllib2, json, time, re, time, datetime, sys, random
from threading import Timer
from difflib import SequenceMatcher

try:
    skype = Skype4Py.Skype()
    skype.Attach()
except Exception:
    print( "Can't attach to Skype." )
    quit()

chats = {
          "test" :  "#lopezloo/$f6d1b455dba8824",
          "mta"  :  "#divx92/$18d4d85908c14588",
          "tr"   :  "#lopezloo/$1df2f3dc7ef04417"
}

def getURL ( url ):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    req = urllib2.Request(url, headers=hdr)

    try:
        page = urllib2.urlopen(req)
    except Exception:
        return

    content = page.read()
    return content

def loadSettings ( ):
    # todo: create default settings file
    global settings
    with open("skype.json") as f:
        settings = json.loads( f.read() )
        f.close()

loadSettings()

def saveSettings ( ):
    with open("skype.json", "w") as f:
        f.write( json.dumps(settings) )
        f.close()

def sendMessageToChat ( chatName, message ):
    for chat in skype.Chats:
        if chat.Name == chatName:
            chat.SendMessage( message )
            return

def OnMessageStatus ( message, status ):
    #if status == 'SENT' or status == 'RECEIVED':
    #print('OnMessageStatus status = ' + str(status) + " msg = " + str(message.Body))
    if status == 'RECEIVED':
        #print( message.Chat.Name )
        print('OnMessageStatus RECEIVED: ' + message.Body.encode('utf-8'))
        if message.Body == "!help" or message.Body == "!pomoc" or message.Body == "!cmd" or message.Body == "!cmds":
            txt = "!twitch [nick]\n!twitchtop [opcjonalnie kategoria] - top streamy z danej kategorii\n!hitbox [nick]\n!topic\n!lines - ilosć linii w kodzie\n!id [pojazd/kategoria]\n!steam\n!ets\n!bandit".decode('utf-8')
            if message.Chat.Name == chats["mta"]:
                txt = txt + "\n!w(iki) [tytuł]".decode('utf-8')
            message.Chat.SendMessage(txt)
            return 

        # Supposed to be current MTA version
        #if message.Body == "!ver":
        #    message.Chat.SendMessage("no ja nie wiem")
        #    return

        # Twitch live status
        if message.Body.find('!twitch ', 0, 8) == 0:
            nick = message.Body[ message.Body.find(' ') + 1 : ]
            sock = urllib.urlopen("https://api.twitch.tv/kraken/streams/" + nick)
            source = sock.read()
            sock.close()
            data = json.loads(source)

            if "status" in data and data["status"] == 404:
                message.Chat.SendMessage("Nie ma takiego kanału.")
                return

            if data["stream"] is not None:
                nick = data["stream"]["channel"]["display_name"]
                game = data["stream"]["game"]
                status = data["stream"]["channel"]["status"]
                viewers = str(data["stream"]["viewers"])
                fps = str( int( round(data["stream"]["average_fps"]) ) )

                if game:
                    message.Chat.SendMessage( nick + " streamuje " + game + " (" + status + ", " + viewers + " widzów, ".decode('utf-8') + fps + " FPS)\nhttps://twitch.tv/" + nick )
                else:
                    message.Chat.SendMessage( nick + " prowadzi stream (" + status + ", " + viewers + " widzów, ".decode('utf-8') + fps + " FPS)\nhttps://twitch.tv/" + nick )
            else:
                message.Chat.SendMessage( nick + " obecnie nic nie streamuje!" )
            return

        # Top Twitch stream from selected category (or in all categories)
        if message.Body.find('!twitchtop', 0, 10) == 0:
            arg_pos = message.Body.find(' ') + 1
            if arg_pos != 0:
                arg = message.Body[ arg_pos : ]
                source = getURL("https://api.twitch.tv/kraken/search/games?type=suggest&live=1&limit=1&q=" + arg)
                data = json.loads(source)

                if len(data["games"]) == 0:
                    message.Chat.SendMessage("Nie ma takiej kategorii.")
                    return

                arg = data["games"][0]["name"]
            else:
                arg = ""

            source = getURL( "https://api.twitch.tv/kraken/streams?limit=3&game=" + arg )
            data = json.loads(source)

            if len(data["streams"]) == 0:
                message.Chat.SendMessage("Brak streamów w kategorii ".decode('utf-8') + arg)
                return

            txt = ""
            for k, stream in enumerate( data["streams"] ):
                nick = stream["channel"]["display_name"]
                status = stream["channel"]["status"]
                viewers = str(stream["viewers"])
                fps = str( int( round(stream["average_fps"]) ) )
                if len(arg) > 0:
                    txt = txt + "\n" + str(k + 1) + ". " + nick + " (" + status + ", " + viewers + " widzów, ".decode('utf-8') + fps + " FPS) https://twitch.tv/" + nick
                else:
                    game = stream["game"]
                    txt = txt + "\n" + str(k + 1) + ". " + nick + " (" + game + ", " + status + ", " + viewers + " widzów, ".decode('utf-8') + fps + " FPS) https://twitch.tv/" + nick

            if len(arg) > 0:
                message.Chat.SendMessage("Top 3 streamów z kategorii ".decode('utf-8') + arg + ":" + txt)
            else:
                message.Chat.SendMessage("Top 3 streamów:".decode('utf-8') + txt)
            return

        # Hitbox live status
        if message.Body.find('!hitbox ', 0, 8) == 0:
            nick = message.Body[ message.Body.find(' ') + 1 : ]
            sock = urllib.urlopen("https://api.hitbox.tv/media/live/" + nick)
            source = sock.read()
            sock.close()
            try:
                data = json.loads(source)
            except Exception:
                message.Chat.SendMessage("Bliżej nieokreślony błąd.")
                return

            if "error" in data:
                message.Chat.SendMessage("Nie ma takiego kanału.")
                return

            nick = data["livestream"][0]["media_display_name"]
            if data["livestream"][0]["media_is_live"] == "0":
                message.Chat.SendMessage(nick + " obecnie nic nie streamuje!")
                return

            game = data["livestream"][0]["category_name"]
            status = data["livestream"][0]["media_status"]
            viewers = data["livestream"][0]["category_viewers"]
            message.Chat.SendMessage( nick + " streamuje " + game + " (" + status + ", " + viewers + " widzów)".decode('utf-8') + "\nhttps://hitbox.tv/" + nick )
            return

        # MTA wiki syntax + link generator
        if (message.Chat.Name == chats["mta"] or message.Chat.Name == chats["test"]) and (message.Body.find('!wiki ', 0, 6) == 0 or message.Body.find('!w ', 0, 3) == 0):
            title = message.Body[ message.Body.find(' ') + 1 : ]
            source = getURL("https://wiki.multitheftauto.com/api.php?action=query&list=search&format=json&prop=revisions&rvprop=content&srsearch=" + title)
            if source is None:
                return
            data = json.loads(source)

            if len(data["query"]["search"]) == 0:
                message.Chat.SendMessage( "Nie ma takiej strony." )
            else:
                page = data["query"]["search"][0]
                txt = "https://wiki.mtasa.com/wiki/" + page["title"].replace(" ", "_")
                
                # Syntax
                sock = urllib.urlopen("https://wiki.multitheftauto.com/api.php?format=json&action=query&prop=revisions&rvprop=content&titles=" + page["title"])
                source = sock.read()
                sock.close()

                data = json.loads(source)

                for k, page in data["query"]["pages"].items():
                    content = page["revisions"][0]["*"]
                    # check if this page is function or event and if is, grab syntax
                    if content.find("function}}") != -1 or content.find("event}}") != -1:

                        header_syntax_start = content.find("Syntax")
                        if header_syntax_start == -1:
                            header_syntax_start = content.find("Parameters")

                        if header_syntax_start != -1:
                            header_syntax_end = content.find("Returns", header_syntax_start)
                            if header_syntax_end == -1:
                                header_syntax_end = content.find("Example", header_syntax_start)
                            if header_syntax_end == -1:
                                header_syntax_end = len(content)

                            syntax_startPos = content.find("<code>[lua", header_syntax_start, header_syntax_end)
                            if syntax_startPos != -1:
                                syntax_startPos = syntax_startPos + 10
                                syntax_startPos = content.find("]", syntax_startPos) + 1

                                syntax_endPos = content.find("</code>", syntax_startPos)
                                syntax = content [ syntax_startPos : syntax_endPos ]
                                syntax = syntax.replace("\n", "")
                                syntax = syntax.replace("  ", "")
                                txt = txt + "\n" + syntax
                            else:
                                # function without parameters
                                txt = txt + "\nbrak parametrów".decode('utf-8')
                message.Chat.SendMessage( txt )

            return

        if message.Body.find('!id ', 0, 4) == 0:
            arg = message.Body[ message.Body.find(' ') + 1 : ]
            findEntityID ( arg, message.Chat.Name )

        # YouTube video title
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
            source = getURL( "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=AIzaSyDViQNqCB7CxTiqS5YiBogXVBykLUtrUmY&id=" + vidID )
            if source is None:
                return
            try:
                data = json.loads(source)

                if len(data["items"]) > 0:
                    title = data["items"][0]["snippet"]["title"]
                    message.Chat.SendMessage('YT: ' + title)
            except Exception:
                return
            return

        # Steam game info
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
            data = getURL( 'http://store.steampowered.com/api/appdetails?appids=' + appID )

            if data is None:
                return

            try:
                data = json.loads( data )
            except Exception:
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
                    currency = "€".decode('utf-8')
                else:
                    currency = "$"

                txt = txt + " " + price1 + "." + price2 + currency
                if data["price_overview"]["discount_percent"] > 0:
                    txt = txt + " [-" + str(data["price_overview"]["discount_percent"]) + "%]"
            message.Chat.SendMessage ( txt )
            return

        # Steam featured games
        if message.Body == '!steam':
            data = getURL('http://store.steampowered.com/api/featured/')
            if not data:
                return

            try:
                data = json.loads( data )
            except Exception:
                return

            txt = "Polecane:\n"
            for game in data["large_capsules"]:
                price1 = str(game["final_price"])[ : -2 ]
                if price1 == "":
                    price1 = "0"
                price2 = str(game["final_price"])[ -2 : ]
                txt = txt + game["name"] + " " + price1 + "." + price2 + "€".decode('utf-8')
                if game["discounted"] and game["discount_percent"] > 0:
                    txt = txt + "[-" + str(game["discount_percent"]) + "%]"
                txt = txt + "\n"
            message.Chat.SendMessage ( txt )
            return

        # TruckersMP various stuff
        if message.Body == '!ets' or message.Body == '!ats':
            # servers status
            data = getURL('https://api.ets2mp.com/servers/')
            if data is None:
                return

            try:
                data = json.loads( data )
            except Exception:
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
            txt = txt + "\nŁącznie ".decode('utf-8') + str(total_players) + "/" + str(total_slots) + " graczy."

            # game time
            data = getURL( 'https://api.ets2mp.com/game_time/' )
            if data is not None:
                try:
                    data = json.loads( data )
                except Exception:
                    return
                if data["error"]:
                    return

                gameTime = datetime.datetime(2015, 10, 25) + datetime.timedelta( minutes = data["game_time"] );
                txt = txt + "\nCzas w grze: " + gameTime.strftime('%H:%M')

            # song at TruckersFM
            data = getURL( 'http://truckers.fm/' )
            if data is not None:
                song_start = data.find( '<span id="currently_playing"> <span id="song"><span class="song-details">' ) + 73
                if song_start != 72:
                    song_end = data.find('</span>', song_start)
                    txt = txt + "\nTruckersFM: " + data [ song_start : song_end ]

            message.Chat.SendMessage ( txt )
            return 

        # MTA community resource name
        if message.Body.find('community.mtasa.com/index.php?p=resources&s=details&id=') >= 0:
            link_start = message.Body.find( 'community.mtasa.com/index.php?set_lang=eng&p=resources&s=details&id=' ) + 55
            link_end = message.Body.find( ' ', link_start )
            if link_end == -1:
                link_end = len(message.Body)

            if link_start >= 0:
                source = getURL( "http://community.mtasa.com/index.php?p=resources&s=details&id=" + message.Body[ link_start : link_end ] )
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


                message.Chat.SendMessage( 'Community: ' + title + " @ " + author + " (" + downloads + " pobrań)".decode('utf-8') )
            return

        if message.Body == '!topic':
            message.Chat.SendMessage( 'Aktualny temat: ' + message.Chat.Topic )
            return

        if message.Body.find('lenny') != -1:
            message.Chat.SendMessage( "( ͡° ͜ʖ ͡°)".decode('utf-8') )
            return

        #if message.Body.find('!stats', 0, 6) == 0:
        #    message.Chat.SendMessage("Statystyki dla chatu " + message.Chat.FriendlyName)
        #    return

        if message.Body.find('!bandit', 0, 8) == 0 or message.Body == "b":
            size_x = 3
            size_y = 3

            arg_pos = message.Body.find(' ') + 1
            if arg_pos != 0 and message.Body [ arg_pos : arg_pos + 1 ] != "":
                size_x = int( message.Body [ arg_pos : arg_pos + 1 ] )

                if message.Body [ arg_pos + 2 : arg_pos + 1 + 2 ] != "":
                    size_y = int( message.Body [ arg_pos + 2 : arg_pos + 1 + 2 ] )

            if size_x < 1:
                size_x = 1
            elif size_x > 8:
                size_x = 8
            if size_y < 1:
                size_y = 1
            elif size_y > 5:
                size_y = 5

            #icons = [ ':)', ':(', ':D', '(cool)', ';)', ':o', '(sweat)', ':|', ':*',
            #':P', '(yn)', '(blush)', ':^)', '(snooze)', '|(', '(inlove)', '(yawn)',
            #'(puke)', '(doh)', '(wasntme)', '(facepalm)', ':S', '(mm)', '8-|',
            #':x', '(wave)', '(devil)', '(envy)', '(makeup)', '(moustache)',
            #'(giggle)', '(clap)', '(think)', '(happy)', '(smirk)',
            #'(nod)', '(shake)', '(emo)', '(tmi)', '(rock)', '(swear)',
            #'(punch)', '(talk)', '(call)',
            #'(wtf)', '(donttalk)' ]

            icons = [ '(heidy)', '(hug)', '(dog)', '(sun)', '(coffee)', '(^)', '(cash)', '(gift)',
            '(tandoori)', '(cheese)', '(d)', '(bell)', '(cat)', '(~)', '(heart)', '(mooning)' ]
            
            txt = ""
            lines = []
            for i in range( 0, size_y ):
                line = []
                for j in range( 0, size_x ):
                    line.insert( j, random.choice(icons) )
                    txt = txt + line[j] + " "
                lines.insert( i, line )
                txt = txt + "\n"

            message = message.Chat.SendMessage( txt )

            for o in range(1, 21):
                time.sleep( 0.2 )
                txt = ""
                for i in reversed(range( 0, size_y )):
                    for j in reversed(range( 0, size_x )):
                        if i > 0:
                            lines[i][j] = lines[i-1][j]
                        else: # 2
                            lines[i][j] = random.choice(icons)
                        txt = txt + lines[i][j] + " "
                    txt = txt + "\n"
                message.Body = txt
            return

        if message.Body.find('!lines', 0, 6) == 0:
            num_lines = sum(1 for line in open('skype.py'))
            num_lines_noempty = sum(1 for line in open('skype.py') if line.rstrip())
            num_comments = sum(1 for line in open('skype.py') if line.find('#') != -1 ) - 2

            message.Chat.SendMessage( "Składam się z ".decode('utf-8') + str(num_lines) + " linii. Wykluczając linie puste, liczba ta spada do ".decode('utf-8') + str(num_lines_noempty) + ". Mój kod zawiera około ".decode('utf-8') + str(num_comments) + " komentarzy." )
            return

        if message.Body == "!btc" or message.Body == "!ltc":
            data = getURL( 'https://www.bitmarket.pl/json/BTCPLN/ticker.json' )
            if data is None:
                return
            try:
                data = json.loads( data )
            except Exception:
                return
            txt = "1 BTC = " + str(data["last"]) + " PLN"            
            data = getURL( 'https://www.bitmarket.pl/json/LTCPLN/ticker.json' )
            if data is None:
                return
            try:
                data = json.loads( data )
            except Exception:
                return
            message.Chat.SendMessage( txt + "\n1 LTC = " + str(data["last"]) + " PLN" )

        if message.Sender.Handle == "lopezloo":
            if message.Body.find("!nick ", 0, 6) == 0:
                arg = message.Body[ message.Body.find(' ') + 1 : ]
                skype.CurrentUser.DisplayName = arg
                message.Chat.SendMessage( "Mój nowy nick to: ".decode('utf-8') + skype.CurrentUser.DisplayName )
                return

            #if message.Body.find("!delast", 0, 7) == 0:
            #    for msg in message.Chat.RecentMessages:
            #        if msg.IsEditable and msg.FromHandle == "lopez.bot":
            #            msg.Body = "x"
            #            return
            #    return

            #if message.Body.find("!delast", 0, 7) == 0:
            #    for msg in message.Chat.RecentMessages:
            #        if msg.IsEditable and msg.FromHandle == "lopez.bot":
            #            msg.Body = "x"
            #            return
            #    return           

    if status == 'RECEIVED' or status == 'SENT':
        if (message.Chat.Name == chats["mta"] or message.Chat.Name == chats["test"]) and message.Body.find('#') != -1:
            bugID_start = message.Body.find('#') + 1
            bugID_end = message.Body.find(' ', bugID_start)
            if bugID_end == -1:
                bugID_end = len(message.Body)
            bugID = message.Body [ bugID_start : bugID_end ]

            name, severity, status = checkMantisBug ( bugID )
            if name is None:
                return

            message.Chat.SendMessage( "[" + severity + "/" + status + "] " + name + "\nhttps://bugs.mtasa.com/view.php?id=" + bugID )
            return
                 
skype.OnMessageStatus = OnMessageStatus

# Disable calls completly (auto refuse every call).
def OnCallStatus ( call, status ):
    if status == "RINGING":
        print( call.PartnerHandle.encode('utf-8') + " calls" )
        try:
            call.Finish(); # this always throw some strange exception but works
        except Exception:
            print('');

skype.OnCallStatus = OnCallStatus

#def OnChatMembersChanged ( chat, members ):
#    chat.SendMessage("OnChatMembersChanged")
    #for member in members:
    #    chat.SendMessage(member.Handle)
#skype.OnChatMembersChanged = OnChatMembersChanged

checkGithub_interval = 60*5 # in sec
def checkGitHub ( ):
    global settings
    print('checkGitHub')
    sock = urllib.urlopen( "https://api.github.com/repos/multitheftauto/mtasa-blue/commits?client_id=29c28b58cce0387e19a5&client_secret=62c2157f307108b637a8258a9f5e6ec549b69fbd&per_page=5" )
    source = sock.read()
    sock.close()
    
    Timer( checkGithub_interval, checkGitHub ).start()

    data = json.loads(source)
    for commit in reversed(data):
        date = commit["commit"]["committer"]["date"]
        commitTime = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").timetuple()) # timestamp
        print( str(commitTime) + " > " + str(settings["lastCommitTime"]) )
        if commitTime > settings["lastCommitTime"]:
            sendMessageToChat( chats["mta"], "[commit] " + commit["commit"]["message"] + " @ " + commit["author"]["login"] + "\n" + commit["html_url"] )
            settings["lastCommitTime"] = commitTime
            saveSettings()

Timer( checkGithub_interval, checkGitHub ).start()

def checkMantisBug ( bugID ):
    source = getURL( "https://bugs.mtasa.com/print_bug_page.php?bug_id=" + str(bugID) )
    if source is None:
        return None, None, None

    if source.find('<td class="form-title">APPLICATION ERROR #') != -1 or source.find("<center><p>Access Denied.</p>") != -1 or source.find('<center><h1>502 Bad Gateway</h1></center>') != -1:
        return None, None, None

    title_startPos = source.find("<title>") + 7
    title_startPos = source.find(":", title_startPos) + 2
    title_endPos = source.find("</title>", title_startPos) - 11
    name = source [ title_startPos : title_endPos ]

    severity_startPos = source.find('<td class="print-category">Severity</td><td class="print">') + 58
    severity_endPos = source.find('</td>', severity_startPos)
    severity = source [ severity_startPos : severity_endPos ]

    status_startPos = source.find('<td class="print-category">Status</td><td class="print">') + 56
    status_endPos = source.find('</td>', status_startPos)
    status = source [ status_startPos : status_endPos ]

    return name, severity, status

def checkMantis ( ):
    name, severity, status = checkMantisBug ( settings["lastBugID"] + 1 )
    if name is not None:
        sendMessageToChat ( chats["mta"], "[" + severity + "/" + status + "] " + name + "\nhttps://bugs.mtasa.com/view.php?id=" + str(settings["lastBugID"] + 1) )
        settings["lastBugID"] = settings["lastBugID"] + 1
        saveSettings ()
    Timer( 60*10, checkMantis ).start()

checkMantis()

# Facepunch Prototypes checker
#def checkPrototypes ( ):
#    data = getURL( "http://prototypes.facepunch.com/" )
#    if data is None:
#        return
#
#    if data.find( '<div id="header">PROTOTYPES REMAINING:') != -1 and data.find( '<div id="header">PROTOTYPES REMAINING: 0</div>' ) == -1:
#        sendMessageToChat ( chats["test"], "lopez, prototypy!\nhttp://prototypes.facepunch.com\n" + data )
#    else:
#        Timer( 60*10, checkPrototypes ).start()
#
#Timer( 60*10, checkPrototypes ).start()

def findEntityID ( name, chatName ):
    with open("vehicles-sa.json") as f:
        try:
            data = json.loads( f.read() )
        except Exception:
            return

        last = { "ratio": 0.0, "type": None, "name": None, "id": None }
        processEntityGroup( data["catalog"]["groups"], name, last )

        print("found " + str(last["name"]) + " (" + str(last["ratio"]) + ")")

        if last["ratio"] < 0.4:
            sendMessageToChat( chatName, "Nic nie znalazłem.".decode('utf-8') )
            return

        if last["type"] == "element":
            txt = last["name"] + " - " + last["id"]
            data = getURL( "https://gta.wikia.com/api.php?action=query&list=search&format=json&prop=revisions&rvprop=content&srlimit=1&srwhat=nearmatch&srsearch=" + last["name"] )
            if data:
                data = json.loads(data)
                if len(data["query"]["search"]) > 0:
                    title = data["query"]["search"][0]["title"].replace(" ", "_")
                    txt = txt + " | https://gta.wikia.com/" + title
            sendMessageToChat( chatName, txt )

        elif last["type"] == "group":
            printEntitiesInGroup( data["catalog"]["groups"], last["name"], chatName )
        else:
            sendMessageToChat( chatName, "Nic nie znalazłem.".decode('utf-8') )

def similarRatio (a, b):
    return SequenceMatcher(None, a, b).ratio()

def processEntityGroup ( groups, searchName, last ):
    for group in groups:
        #print(group["name"])
        ratio = similarRatio( group["name"], searchName )
        if ratio > last["ratio"]:
            last["ratio"] = ratio
            last["name"] = group["name"]
            last["type"] = "group"
            last["id"] = None
            #print( str(last["name"]) + " " + str(last["ratio"]) )

        if "group" in group:
            processEntityGroup ( group["group"], searchName, last )
        elif "vehicle" in group:
            # elements
            for element in group["vehicle"]:
                ratio = similarRatio( element["name"], searchName )
                if ratio > last["ratio"]:
                    last["ratio"] = ratio
                    last["name"] = element["name"]
                    last["type"] = "element"
                    last["id"] = element["id"]
                    
                    #print( str(last["name"]) + " " + str(last["ratio"]) )

def printEntitiesInGroup ( groups, groupName, chatName ):
    for group in groups:
        #print(group["name"])
        if group["name"] == groupName:
            #print(group["name"] + " goood!")
            if "group" in group:
                txt = "Podgrupy w grupie " + groupName + ":\n"
                for group in group["group"]:
                    txt = txt + " > " + group["name"]
                sendMessageToChat( chatName, txt )
            elif "vehicle" in group:
                txt = "Pojazdy w grupie " + groupName + ":\n"
                for element in group["vehicle"]:
                    txt = txt + " > " + element["name"] + " - " + element["id"] + "\n"
                sendMessageToChat( chatName, txt )
            return
        elif "group" in group:
            printEntitiesInGroup ( group["group"], groupName, chatName )
    return

# Listener r/freegamesonsteam
def checkFreeGamesSubreddit ( ):
    global settings
    Timer( 60*1, checkFreeGamesSubreddit ).start()

    data = getURL( "https://www.reddit.com/r/freegamesonsteam/new.json?limit=1" )
    if data is None:
        return

    try:
        data = json.loads(data)
    except Exception:
        return

    if "data" not in data:
        return

    for link in data["data"]["children"]:
        if link["data"]["created_utc"] > settings["lastFGTime"]:
            sendMessageToChat ( chats["tr"], link["data"]["title"] + "\nhttps://reddit.com" + link["data"]["permalink"] )
            settings["lastFGTime"] = link["data"]["created_utc"]
            saveSettings()

Timer( 60*1, checkFreeGamesSubreddit ).start()

input("Skype bot started.\n")
