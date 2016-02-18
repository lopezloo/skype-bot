# -*- coding: utf-8 -*-
from threading import Timer
import time, datetime
import skype
import utils

checkGithub_interval = 60*5
def checkGitHub ( ):
    print('checkGitHub')
    
    Timer( checkGithub_interval, checkGitHub ).start()
    data = utils.getJSON( "https://api.github.com/repos/multitheftauto/mtasa-blue/commits?client_id=29c28b58cce0387e19a5&client_secret=62c2157f307108b637a8258a9f5e6ec549b69fbd&per_page=5" )
    if data is None:
        return

    for commit in reversed(data):
        date = commit["commit"]["committer"]["date"]
        commitTime = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").timetuple()) # timestamp
        print( str(commitTime) + " > " + str(utils.g_settings["lastCommitTime"]) )
        if commitTime > utils.g_settings["lastCommitTime"]:
            skype.sendMessageToChat( skype.g_chats["mta"], "[commit] " + commit["commit"]["message"] + " @ " + commit["author"]["login"] + "\n" + commit["html_url"] )
            utils.g_settings["lastCommitTime"] = commitTime
            utils.saveSettings()


def checkMantisBug ( bugID ):
    source = utils.getURL( "https://bugs.mtasa.com/print_bug_page.php?bug_id=" + str(bugID) )
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
    name, severity, status = checkMantisBug ( utils.g_settings["lastBugID"] + 1 )
    if name is not None:
        skype.sendMessageToChat ( skype.g_chats["mta"], "[" + severity + "/" + status + "] " + name + "\nhttps://bugs.mtasa.com/view.php?id=" + str(utils.g_settings["lastBugID"] + 1) )
        utils.g_settings["lastBugID"] = utils.g_settings["lastBugID"] + 1
        utils.saveSettings ()
    Timer( 60*10, checkMantis ).start()

# todo do it dynamic per chat
# Listener r/freegamesonsteam
def checkFreeGamesSubreddit ( ):
    Timer( 60*1, checkFreeGamesSubreddit ).start()

    data = utils.getJSON( "https://www.reddit.com/r/freegamesonsteam/new.json?limit=1" )
    if data is None or "data" not in data:
        return

    for link in data["data"]["children"]:
        if link["data"]["created_utc"] > utils.g_settings["lastFGTime"]:
            skype.sendMessageToChat ( skype.g_chats["tr"], link["data"]["title"] + "\nhttps://reddit.com" + link["data"]["permalink"] )
            utils.g_settings["lastFGTime"] = link["data"]["created_utc"]
            utils.saveSettings()


def initNotifications():
    print("initNotifications")
    Timer( checkGithub_interval, checkGitHub ).start()
    Timer( 60*10, checkMantis ).start()
    Timer( 60*1, checkFreeGamesSubreddit ).start()
