import json
import base64

def main(q):

	# Decode the arguments passed by Alfred.
	# The result is a dictionary with keys 'type', 'value', and 'notification'.
	args = json.loads(base64.b64decode(q))

	t = args['type']
	v = args['value']
	n = args['notification']

	#
	# Act on the various types.
	#

	# Open an URL in the default browser.
	if t == 'url':
		import webbrowser
		webbrowser.open(v)

	# Past to clipboard.
	elif t == 'clipboard':
		import os
		import alp
		import subprocess
		# Paste to the clipboard via the command line util 'pbcopy'.
		# First, write the data to a file which 'pbcopy' will read.
		cpf = os.path.join(alp.cache(),"clipboard.txt")
		with open(cpf, "w") as f:
			f.write(v)
		# Now call 'pbcopy'.
		subprocess.call('pbcopy < "' + cpf + '"',shell=True)

	# Lookup Inspire record.
	elif t == 'inspirerecord':

		import urllib
		import webbrowser
		import xml.etree.ElementTree as ET

		# First, get the URL for the record by querying Inspire.

		# Get XML data from Inspire.
		url = "http://inspirehep.net/rss?" + urllib.urlencode({'ln':'en','p':v})
		try:
			f = urllib.urlopen(url)
			xml = f.read()
			f.close()
		except:
			return
		# Parse the XML.
		e = ET.fromstring(xml)
		for item in e.iter('item'):
			for link in item.iter('link'):
				recordurl = link.text
				break
			break

		# Now open the URL.
 		webbrowser.open(recordurl)

 	elif t == 'clearcache':
		import os
		import alp

		# Remove cache files from storage folder.
		for f in os.listdir(alp.storage()):
			file_path = os.path.join(alp.storage(), f)
			try:
				if os.path.isfile(file_path):
					if os.path.splitext(f)[-1] == ".cache":
						os.remove(file_path)
			except Exception, e:
				print e

	elif t == 'setlocaldir':
		import alp

		settings = alp.Settings()
		settings.set(local_dir=v)

	elif t == 'open':
		import os
		os.system("open '" + v + "'")

 	# If the notification is not empty, issue it.
	if n != {}:
		from alp.notification import Notification

		if 'title' in n:
			title = n['title']
		else:
			title = ""
		if 'subtitle' in n:
			subtitle = n['subtitle']
		else:
			subtitle = ""
		if 'text' in n:
			text = n['text']
		else:
			text = ""

		notification = alp.notification.Notification()
		notification.notify(title, subtitle, text)

	
