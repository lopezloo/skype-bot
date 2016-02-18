# -*- coding: utf-8 -*-
import utils, skype
from commands import Command

from difflib import SequenceMatcher
import json

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
            skype.sendMessageToChat( chatName, "Nic nie znalazłem." )
            return

        if last["type"] == "element":
            txt = last["name"] + " - " + last["id"]
            data = utils.getURL( "https://gta.wikia.com/api.php?action=query&list=search&format=json&prop=revisions&rvprop=content&srlimit=1&srwhat=nearmatch&srsearch=" + last["name"] )
            if data:
                data = json.loads(data)
                if len(data["query"]["search"]) > 0:
                    title = data["query"]["search"][0]["title"].replace(" ", "_")
                    txt = txt + " | https://gta.wikia.com/" + title
            skype.sendMessageToChat( chatName, txt )

        elif last["type"] == "group":
            printEntitiesInGroup( data["catalog"]["groups"], last["name"], chatName )
        else:
            skype.sendMessageToChat( chatName, "Nic nie znalazłem." )

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
                skype.sendMessageToChat( chatName, txt )
            elif "vehicle" in group:
                txt = "Pojazdy w grupie " + groupName + ":\n"
                for element in group["vehicle"]:
                    txt = txt + " > " + element["name"] + " - " + element["id"] + "\n"
                skype.sendMessageToChat( chatName, txt )
            return
        elif "group" in group:
            printEntitiesInGroup ( group["group"], groupName, chatName )
    return

def cmd_id ( chat, entityName ):
    findEntityID ( entityName, chat.Name )
Command ( "!id", cmd_id )
