# -*- coding: utf-8 -*-
# The above is necessary because the delimiter (see below) is a unicode character.

import alp

settings = alp.Settings()

# Set the delimiter for faking a context menu in Alfred.
alfred_delim = unicode(" ► ",'utf-8')

def main(q=""):
    """Refers to one of the main methods."""

    search      = q.decode('utf-8')
    num_delims  = search.count(alfred_delim)
    searchsplit = search.split(alfred_delim)

    # If the user hasn't typed anything, give some instructions and the
    # option to open the settings menu.
    if search.strip() == "":
        result = [
            alp.Item(
                title        = "Search INSPIRE",
                subtitle     = "Begin typing to search INSPIRE",
                valid        = "no",
                autocomplete = ""
            ),
            alp.Item(
                title        = "Settings",
                subtitle     = "Change ainspire's settings",
                valid        = "no",
                autocomplete = "settings" + alfred_delim
            )
        ]
    # Settings menu.
    elif searchsplit[0] == "settings":
        result = settings_menu(searchsplit[1:])
    # If the search has no delimiters the user is still typing the query:
    elif num_delims == 0:
        result = typing_menu(searchsplit[0])
    # Has the string one delimiter? Then perform a regular Inspire search.
    elif num_delims == 1:
        result = inspire_search(searchsplit[0].strip())
    # Are there two delimiters? Then it's a context menu.
    elif num_delims == 2:
        result = context_menu(searchsplit[1],searchsplit[0])
    # Three delimiters? Then it's an author search menu.
    elif num_delims == 3:
        result = author_menu(searchsplit[2])

    return alp.feedback(result)


def typing_menu(search=""):
    return alp.Item(
        title        = "Search INSPIRE for '" + search + "'",
        subtitle     = "Action this item to search INSPIRE",
        valid        = "no",
        autocomplete = search + alfred_delim
    )
#
# Functions for accessing and changing settings
#

def settings_menu(q={}):
    """Returns a settings menu."""
    # Main settings
    if q[0] == "":
        return main_settings()
    # Dialog for changing the directory
    if q[0] == "setdir":
        return set_local_dir(q[1])
    if q[0] == "setcache":
        return set_cache(q[1])

def main_settings():
    """Returns the main settings menu"""
    menuitems = []
    # Option to clear the cache.
    menuitems.append(
        alp.Item(
            title="Clear INSPIRE cache",
            subtitle="Clears all cached INSPIRE searches",
            arg=encode_arguments(
                type="clearcache",
                notification={
                    'title':'Cache cleared',
                    'text':'All saved INSPIRE results have been cleared'
                }
            )
        )
    )

    # Option to change the cache setting
    menuitems.append(
        alp.Item(
            title="Change cache setting",
            subtitle="Set the time INSPIRE searches are cached",
            valid="no",
            autocomplete="settings" + alfred_delim + "setcache" + alfred_delim
        )       
    )

    # Option to toggle the local search
    local_search_setting = get_local_search_setting()
    if local_search_setting:
        titlepre = "Disable"
        subtitle = "Only give results from INSPIRE"
    else:
        titlepre = "Enable"
        subtitle = "Search local directory for PDFs before completing queries with '.'"
    menuitems.append(
        alp.Item(
            title=titlepre + " local search",
            subtitle=subtitle,
            arg=encode_arguments(
                type="setting",
                value={'local_search':not local_search_setting},
                notification={
                    'title':'Setting changed',
                    'text':titlepre+'d local search'
                }
            )
        )       
    )

    # Option to change the local directory
    menuitems.append(
        alp.Item(
            title="Change local directory",
            subtitle="Set local directory where PDFs are stored and searched",
            valid="no",
            autocomplete="settings" + alfred_delim + "setdir" + alfred_delim
        )       
    )

    return menuitems

def set_cache(q=""):
    if q=="":
        return alp.Item(
            title="Begin typing to set the cache timeout",
            subtitle="Current value is " + str(get_cache_setting()) + " days",
            valid="no"
        )
    try:
        s=str(int(q))
    except:
        s="0"
    return alp.Item(
        title="Set cache timeout to " + s + " days",
        subtitle="Current value is " + str(get_cache_setting()) + " days",
        arg=encode_arguments(
            type="setting",
            value={'cache':int(s)},
            notification={
                'title':'Setting changed',
                'text':'Cache timeout set to ' + s + ' days'
            }
        )
    )

def set_local_dir(q=""):
    """Sets the local directory"""
    import os

    actions = []

    # Use mdfind to search for a directory within ~/
    if q=="":
        actions.append(alp.Item(
            title="Begin typing to search for a directory",
            subtitle="All directories in " + os.path.expanduser("~") +" will be searched",
            valid="no"
        ))
    else:
        mdfindresults = alp.find("-onlyin ~ 'kMDItemFSName=\"*"+q+"*\"c && kMDItemContentType==public.folder'")
        for mdfindresult in mdfindresults:
            actions.append(
                alp.Item(
                    title=mdfindresult,
                    subtitle="Set the local directory to " + mdfindresult,
                    arg=encode_arguments(
                        type="setting",
                        value={'local_dir':mdfindresult},
                        notification={
                            'title':'Setting changed',
                            'text':'Local directory set to ' + mdfindresult
                        }
                    )
                )
            )

    # Also remind the user what the current directory is.
    actions.append(alp.Item(
        title="Current local directory",
        subtitle=get_local_dir(),
        valid="no" 
    ))

    return actions


def get_local_dir():
    """Returns the local directory for storing and searching PDFs"""
    import os
    localdir = settings.get("local_dir", default=os.path.expanduser("~/Downloads"))
    if not os.path.exists(localdir):
        os.makedirs(localdir)
    return localdir

def get_local_search_setting():
    return settings.get("local_search", default=False)

def get_cache_setting():
    return settings.get("cache", default=7)

#
# The main functions are below.
#

def local_search(search=""):
    """Performs a local search"""

    import os

    words       = search.lower().split(" ")
    ldir        = get_local_dir()
    files       = []
    fileitems   = []

    # Get all files in the local directory.
    for (dirpath, dirnames, filenames) in os.walk(ldir):
        files.extend(filenames)
        break
    # Loop over them to fill 'fileitems'.
    for f in files:
        filename, ext = os.path.splitext(f)
        filenamelower = filename.lower()
        if ext != ".pdf":
            continue
        # Search for the words in the input query
        match = True
        for word in words:
            if word not in filenamelower:
                match = False
                break
        if not match:
            continue
        # Make the alp item.
        filenamesplit = filename.split(" - ")
        fileitems.append(alp.Item(
            title    = filenamesplit[1],
            subtitle = filenamesplit[0],
            type     = 'file',
            icon     = "com.adobe.pdf",
            fileType = True,
            uid      = filename,
            arg      = encode_arguments(
                type    = "open",
                value   = os.path.join(ldir, f)
            )
        ))
    # Lastly, append an alp item that searches INSPIRE
    fileitems.append(alp.Item(
        title    = "Search INSPIRE for '" + search + "'",
        subtitle = "Searches the INSPIRE database",
        arg      = encode_arguments(
            type    = "inspiresearch",
            value   = search 
        )
    ))
    # And return.
    return alp.feedback(fileitems)

def inspire_search(search=""):
    """Searches Inspire."""

    import time
    import shutil
    import os
    import json
    import base64

    # Path for the temporary bibtex results.
    tempf = os.path.join(alp.cache(),"results.bib")
    # Path for the temporary latest parsed results.
    lastf = os.path.join(alp.cache(),"lastresults.json")
    # Path for the permanent cache of the query. Note the urlsafe encode.
    savef = os.path.join(alp.storage(),base64.urlsafe_b64encode(search) + ".cache")

    # Check if cache file exists, and if it's not older than a week.
    try:
        # Get the modificiation time of the cache file.
        mt = os.path.getmtime(savef)
        # Get the current time.
        ct = time.time()
        # Is the difference in time less a number of days? Then use it as cache.
        usecache =  ct - mt < ( get_cache_setting() * 86400 )
    except:
        # If the above fails (e.g. when the file doesn't exist), don't use cache.
        usecache = False

    if usecache:
        # Read the cache file and parse the JSON to a dictionary.
        with open(savef,"r") as f:
            bibitems = json.load(f)
    else:
        from bibtexparser.bparser import BibTexParser
        from pyinspire import pyinspire
        # Query Inspire and get the result in form of BibTeX.
        bibtex = pyinspire.get_text_from_inspire(search,"bibtex").encode('utf-8')
        # Write the BibTeX to a file.
        with open(tempf,"w") as f:
            f.write(bibtex)
        # Parse the BibTeX from the same file.
        with open(tempf,"r") as f:
            bp = BibTexParser(f)
        # Get the bibtex as a dictionary and remove any newlines.
        bibitems = map(remove_newlines,bp.get_entry_list())
        # Save the dictionary to the cache file.
        with open(savef,"w") as f:
            json.dump(bibitems,f)

    # Copy the cache file to the file contained the lastest results.
    shutil.copy(savef,lastf)

    # Parse the result dictionary to alp items.
    alpitems = []
    for bibitem in bibitems:
        alpitems.append(bibitem_to_alpitem(bibitem,search))

    # No results? Then tell the user, and offer to search the Inspire website.
    if len(alpitems) == 0:
        import urllib
        alpitems.append(alp.Item(
            title       = "No results",
            subtitle    = "Search on the INSPIRE website for '" + search + "'",
            arg=encode_arguments(
                type    = 'url',
                value   = "http://inspirehep.net/search?ln=en&" + urllib.urlencode({'p':search})
            )
        ))

    # And return feedback for Alfred.
    return alpitems


def context_menu(key="",search=""):
    """Returns the context menu for a result item"""

    # This method takes only the key (id) of the actioned item as an argument.
    # So we need to load the last results, and find the item of that key.

    import os
    import json
    import time

    bid = alp.bundle() + str(time.time()) 

    # Load the parsed results from the latest Inspire search.
    lastf = os.path.join(alp.cache(),"lastresults.json")
    with open(lastf,"r") as f:
        items = json.load(f)

    # Lookup the item from the results.
    for i in items:
        if 'id' in i:
            if i['id'] == key:
                item = i
                break

    # Populate the context menu action list.
    actions = []

    # Link to the Inspire record page.
    actions.append(
        alp.Item(
            title    = item['title'],
            subtitle = "Open INSPIRE record page in browser",
            arg      = encode_arguments(type='inspirerecord',value=item['id']),
            uid      = bid+"inspirerecord"
        )
    )

    # Author search.
    authors = item['author'].split(" and ")
    if len(authors) == 1:
        actions.append(
            alp.Item(
                title        = item['author'],
                subtitle     = "Find more papers of author",
                valid        = "no",
                autocomplete = "find a "+ item['author'] + alfred_delim,
                uid          = bid + "authors"
            )
        )
    else:
        actions.append(
            alp.Item(
                title        = authors_to_lastnames(item['author']),
                subtitle     = "Find more papers of authors",
                valid        = "no",
                autocomplete = search + alfred_delim + key + alfred_delim + item['author'] + alfred_delim,
                uid          = bid + "authors"
            )
        )   

    # Link to resolve the DOI.
    if 'doi' in item:
        url = "http://dx.doi.org/" + item['doi']
        actions.append(
            alp.Item(
                title    = bibitem_to_journaltext(item),
                subtitle = "Open DOI in browser",
                arg      = encode_arguments(type='url',value=url),
                uid      = bid + "doi"
            )
        )

    # Next, the option to open the PDF from arXiv.
    if 'eprint' in item:
        if item['archiveprefix'] != 'arXiv':
            urlprefix = item['archiveprefix'] + "/"
            prefix = urlprefix
        else:
            urlprefix = ""
            prefix = 'arXiv:'
        url = "http://arxiv.org/pdf/" + urlprefix + item['eprint']
        filename = os.path.join(
            get_local_dir(),
            (item['eprint'] + " " + authors_to_lastnames(item['author']) + " - " + item['title'] + '.pdf').replace('/','_').replace(':','_')
        )
        actions.append(
            alp.Item(
                title    = prefix + item['eprint'],
                subtitle = "Download and open PDF",
                arg      = encode_arguments(type='getpdf',value=[url,filename]),
                uid      = bid + "arxivpdf"
            )
        )

    # The option to lookup references.
    actions.append(
        alp.Item(
            title        = "References",
            subtitle     = "Find papers that this paper cites",
            valid        = "no",
            autocomplete = "citedby:" + key + alfred_delim,
            uid          = bid + "refs"
        )
    )

    # The option to lookup citations.
    actions.append(
        alp.Item(
            title        = "Citations",
            subtitle     = "Find papers that cite this paper",
            valid        = "no",
            autocomplete = "refersto:" + key + alfred_delim,
            uid          = bid + "cites"
        )
    )

    # The option to copy the bibtex of the current item to the clipboard.
    actions.append(
        alp.Item(
            title       = "BibTeX",
            subtitle    = "Copy BibTeX to clipboard",
            uid         = bid+"bibtex",
            arg         = encode_arguments(
                type         = 'clipboard',
                value        = bibitem_to_bibtex(item),
                notification = {
                    'title':'Copied BibTeX to clipboard',
                    'text':'BibTeX for ' + key + ' has been copied to the clipboard'
                }
            )
        )
    )

    # And return.
    return actions


def author_menu(authors=""):
    """Returns an Alfred context menu populated with authors"""

    # Split the string into single authors.
    authorlist  = authors.split(" and ")

    # Populate the action list.
    actions = []
    for a in authorlist:
        if a == "others":
            aitem = alp.Item(
                title    = "More authors",
                subtitle = "Open the INSPIRE page for all authors of the paper",
                arg      = encode_arguments(type='inspirerecord',value=bibid)
            )
        else:
            aitem = alp.Item(
                title        = a,
                subtitle     = "Find more papers of author",
                valid        = "no",
                autocomplete = "find a "+ a + alfred_delim
            )
        actions.append(aitem)

    # And return.
    return actions

#
# Auxiliary functions below.
#

def remove_newlines(bib):
    """Removes all newlines with spaces in the values of a dictionary result item"""
    for key in bib:
        bib[key] = bib[key].replace('\n',' ')
    return bib

def bibitem_to_alpitem(bib, search):
    """Converts a dictionary result item to an alp item"""

    # Prepend the year to the subtitle if it's there.
    if 'eprint' in bib:
        subpre = bib['eprint'] + " "
    elif 'year' in bib:
        subpre = bib['year'] + " "
    else:
        subpre = ""

    # Append the journal to the subtitle if it's there.
    journaltext = bibitem_to_journaltext(bib)
    if journaltext != "":
        subpost = " (" + journaltext + ")"
    else:
        subpost = ""

    # Construct an alp item and return.
    return alp.Item(
        title           = bib['title'].replace('\n',' '),
        subtitle        = subpre + authors_to_lastnames(bib['author']) + subpost,
        valid           = "no", # This is to fake the contextual menu.
        autocomplete    = search + alfred_delim + bib['id'] + alfred_delim # Same here.
    )


def bibitem_to_journaltext(bib):
    """Returns 'Journal volume p.xx-yy' or the DOI"""
    if 'journal' in bib:
        t = bib['journal']
        if 'volume' in bib:
            t += " " + bib['volume']
            if 'pages' in bib:
                t += " p." + bib['pages']
    else:
        if 'doi' in bib:
            t = bib['doi']
        else:
            t = ""
    return t


def bibitem_to_bibtex(bib):
    """Converts a dictionary result item to bibtex"""
    bibtex = "@" + bib['type'] + "{" + bib['id'] + ",\n"
    max_len = 0
    for key in bib:
        if len(key) > max_len:
            max_len = len(key)
    for key in bib:
        if key == 'type' or key == 'id':
            continue
        bibtex += "      " + key + ( (max_len - len(key)) * " " ) + " = "
        if(key == 'title'):
            bibtex += '"{'+bib[key]+'}"'
        else:
            bibtex += '"'+bib[key]+'"'
        bibtex += ",\n"
    bibtex += "}"

    return bibtex


def authors_to_lastnames(authors):
    """Strips the first names from the bibtex author list"""
    lastnames = map(get_lastname,authors.split(" and "))
    if len(lastnames) == 0:
        return ""
    if len(lastnames) == 1:
        return lastnames[0]
    if len(lastnames) == 2:
        return lastnames[0] + " and " + lastnames[1]
    return ", ".join(lastnames[0:-1]) + ", and " + lastnames[-1]


def get_lastname(name):
    """Auxiliary function for authors_to_lastnames"""
    names = name.split(",")
    return names[0]


def encode_arguments(type="clipboard",value="",notification={}):
    """Encodes arguments for Alfred that can be passed along to the action script"""
    import json
    import base64
    # Return the base64 encoded JSON dump of a dictionary.
    return base64.b64encode(json.dumps({
        'type': type,
        'value': value,
        'notification': notification
    }))