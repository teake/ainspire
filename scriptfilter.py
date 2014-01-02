# -*- coding: utf-8 -*-
# The above is necessary because the delimiter (see below) is a unicode character.

import alp

# Set the delimiter for faking a context menu in Alfred.
alfred_delim = unicode("►",'utf-8')

def main(q=""):
	"""Main method."""
	search = q.decode('utf-8').strip()
	num_delims = search.count(alfred_delim)
	# Has the string no delimiter? Then perform a regular Inspire search.
	if num_delims == 0:
		return query_inspire(search)
	# Is there one delimiter? Then it's a context menu.
	if num_delims == 1:
		return context_menu(search)
	# Two delimiters? Then it's a author search menu.
	if num_delims == 2:
		return author_menu(search)

#
# The two main sub functions are below.
#

def query_inspire(search=""):
	"""Searches Inspire."""

	# First check if the search query ends in "." (which marks a full query).
	# If not, inform the user and offer to complete the query with a full stop.
	if search[-1] != "." :
		return alp.feedback(alp.Item(
			title="Search for '" + search + "'",
			subtitle="Or end the query with a full stop (.) to search",
			valid="no",
			autocomplete=search + "."
		))
	else:
		q = search[:-1]

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
	savef = os.path.join(alp.storage(),base64.urlsafe_b64encode(q))

	# Check if cache file exists, and if it's not older than a week.
	try:
		# Get the modificiation time of the cache file.
		mt = os.path.getmtime(savef)
		# Get the current time.
		ct = time.time()
		# Is the difference in time less than a week? Then use it as cache.
		usecache =  ct - mt < 604800
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
		bibtex = pyinspire.get_text_from_inspire(q,"bibtex").encode('utf-8')
		# Write the BibTeX to a file.
		with open(tempf,"w") as f:
			f.write(bibtex)
		# Parse the BibTeX from the same file.
		with open(tempf,"r") as f:
			bp = BibTexParser(f)
		# Get the bibtex as a dictionary.
		bibitems = bp.get_entry_dict()
		# Save the dictionary to the cache file.
		with open(savef,"w") as f:
			json.dump(bibitems,f)

	# Copy the cache file to the file contained the lastest results.
	shutil.copy(savef,lastf)

	# Parse the result dictionary to alp items.
	alpitems = []
	for key in bibitems:
		alpitems.append(bibitem_to_alpitem(bibitems[key]))

	# No results? Then tell the user, and offer to search the Inspire website.
	if len(alpitems) == 0:
		import urllib
		alpitems.append(alp.Item(
			title="No results",
			subtitle="Search on the Inspire website for " + q + ".",
			arg=encode_arguments(
				'url',
				"http://inspirehep.net/search?ln=en&" + urllib.urlencode({'p':q})
			)
		))

	# And return feedback for Alfred.
	return alp.feedback(alpitems)


def context_menu(search=""):
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
		dicts = json.load(f)

	# Get the key from the search query.
	key = search.split(alfred_delim)[0].strip()

	# Lookup the item from the results.
	item = dicts[key]

	# Populate the context menu action list.
	actions = []

	# Link to the Inspire record page.
	actions.append(
		alp.Item(
			title=item['title'],
			subtitle="Open Inspire record page",
			arg=encode_arguments('inspirerecord',item['id']),
			uid=bid+"inspirerecord"
		)
	)

	# Author search.
	authors = item['author'].split(" and ")
	if len(authors) == 1:
		actions.append(
			alp.Item(
				title=item['author'],
				subtitle="Find more papers of author",
				valid="no",
				autocomplete="find a "+ item['author'].replace('\n',' ') + ".",
				uid=bid+"authors"
			)
		)
	else:
		actions.append(
			alp.Item(
				title=authors_to_lastnames(item['author']),
				subtitle="Find more papers of authors",
				valid="no",
				autocomplete=search + " " + item['author'].replace('\n',' ') + " " + alfred_delim,
				uid=bid+"authors"
			)
		)	

	# Link to resolve the DOI.
	if 'doi' in item:
		url = "http://dx.doi.org/" + item['doi']
		actions.append(
			alp.Item(
				title=bibitem_to_journaltext(item),
				subtitle="Open DOI in browser",
				arg=encode_arguments('url',url),
				uid=bid+"doi"
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
		actions.append(
			alp.Item(
				title=prefix + item['eprint'],
				subtitle="Open PDF in browser",
				arg=encode_arguments('url',url),
				uid=bid+"arxivpdf"
			)
		)

	# The option to lookup references.
	actions.append(
		alp.Item(
			title="References",
			subtitle="Find papers that this paper cites",
			valid="no",
			autocomplete="citedby:" + key + ".",
			uid=bid+"refs"
		)
	)

	# The option to lookup citations.
	actions.append(
		alp.Item(
			title="Citations",
			subtitle="Find papers that cite this paper",
			valid="no",
			autocomplete="refersto:" + key + ".",
			uid=bid+"cites"
		)
	)

	# The option to copy the bibtex of the current item to the clipboard.
	actions.append(
		alp.Item(
			title="BibTeX",
			subtitle="Copy BibTeX to clipboard",
			arg=encode_arguments('clipboard',bibitem_to_bibtex(item),"BibTeX copied to clipboard"),
			uid=bid+"bibtex"
		)
	)

	# And return.
	return alp.feedback(actions)


def author_menu(search=""):
	"""Returns an Alfred context menu populated with authors"""

	# Get the string containing all authors.
	authors 	= search.split(alfred_delim)[1].strip()
	# Split the string into single authors.
	authorlist 	= authors.split(" and ")

	# Populate the action list.
	actions = []
	for a in authorlist:
		actions.append(
			alp.Item(
				title=a,
				subtitle="Find more papers of author",
				valid="no",
				autocomplete="find a "+ a + "."
			)
		)

	# And return.
	return alp.feedback(actions)

#
# Auxiliary functions below.
#

def bibitem_to_alpitem(bib):
	"""Converts a dictionary result item to an alp item"""

	# Prepend the year to the subtitle if it's there.
	if 'year' in bib:
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
		title			= bib['title'],
		subtitle		= subpre + authors_to_lastnames(bib['author']) + subpost,
		valid			= "no", # This is to fake the contextual menu.
		autocomplete	= bib['id'] + " " + alfred_delim # Same here.
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
	bibtex = "@" + bib['type'] + "{" + bib['id'] + "\n"
	for key in bib:
		if key == 'type' or key == 'id':
			continue
		bibtex += "      " + key + " = "
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


def encode_arguments(type="clipboard",value="",notification=""):
	"""Encodes arguments for Alfred that can be passed along to the action script"""
	import json
	import base64
	# Return the base64 encoded JSON dump of a dictionary.
	return base64.b64encode(json.dumps({
		'type': type,
		'value': value,
		'notification': notification
	}))