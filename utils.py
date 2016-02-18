# -*- coding: utf-8 -*-
import urllib, urllib2, time, re, time, datetime, json

g_debug = True

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

    return page.read()

def getJSON ( url ):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'application/json',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    req = urllib2.Request(url, headers=hdr)
    try:
        page = urllib2.urlopen(req)
        data = json.loads( page.read() )
    except Exception:
        return
    return data

def loadSettings ( ):
    # todo: create default settings file
    global g_settings
    print("loadSettings")
    with open("skype.json") as f:
        g_settings = json.loads( f.read() )
        f.close()

def saveSettings ( ):
    with open("skype.json", "w") as f:
        f.write( json.dumps(g_settings) )
        f.close()
