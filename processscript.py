import json
import base64

def main(q):

	# Decode the arguments passed by Alfred.
	# The result is a dictionary with keys 'type', 'value', and 'notification'.
	args = json.loads(base64.b64decode(q))

	#
	# Act on the various types.
	#

	# Open an URL in the default browser.
	if args['type'] == 'url':
		import webbrowser
		webbrowser.open(args['value'])

	# Past to clipboard.
	if args['type'] == 'clipboard':
		import os
		import alp
		import subprocess
		# Paste to the clipboard via the command line util 'pbcopy'.
		# First, write the data to a file which 'pbcopy' will read.
		cpf = os.path.join(alp.cache(),"clipboard.txt")
		with open(cpf, "w") as f:
			f.write(args['value'])
		# Now call 'pbcopy'.
		subprocess.call('pbcopy < "' + cpf + '"',shell=True)

	# Lookup Inspire record.
	if args['type'] == 'inspirerecord':

		import urllib
		import webbrowser
		import xml.etree.ElementTree as ET

		# First, get the URL for the record by querying Inspire.

		# Get XML data from Inspire.
		url = "http://inspirehep.net/rss?" + urllib.urlencode({'ln':'en','p':args['value']})
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

 	# If the notification is not empty, issue it.
	if args['notification'] != "":
		from alp.notification import Notification
		n = alp.notification.Notification()
		n.notify(args['notification'], "", "")

	
