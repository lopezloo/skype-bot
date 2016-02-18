# -*- coding: utf-8 -*-
import utils, skype
from commands import Command

# MTA wiki syntax + link generator
def cmd_mtawiki ( chat, title ):
    data = utils.getJSON( "https://wiki.multitheftauto.com/api.php?action=query&list=search&format=json&prop=revisions&rvprop=content&srsearch=" + title )
    if data is None:
        return

    if len(data["query"]["search"]) == 0:
        skype.sendMessageToChat( chat, "Nie ma takiej strony." )
        return

    page = data["query"]["search"][0]
    txt = "https://wiki.mtasa.com/wiki/" + page["title"].replace(" ", "_")
    
    # Syntax
    data = utils.getJSON( "https://wiki.multitheftauto.com/api.php?format=json&action=query&prop=revisions&rvprop=content&titles=" + page["title"] )
    if data is None:
        return

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
                    txt = txt + "\nbrak parametrów"
        skype.sendMessageToChat( chat, txt )

Command ( "!wiki", cmd_mtawiki )
Command ( "!w", cmd_mtawiki )