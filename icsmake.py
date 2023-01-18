from ics import Calendar, Event
from bs4 import BeautifulSoup
import argparse
import requests
from pathlib import Path



def fetch_html(url, cachefilename="index.html"):
	htmlfile = Path(cachefilename)

	if not htmlfile.exists():
		
		response = requests.get(url)
		with htmlfile.open("w") as f:
			f.write(response.text)

def parse_html(cachefilename="index.html"):
	htmlfile = Path(cachefilename)
	html = htmlfile.read_text()
	soup = BeautifulSoup(html)

	c = Calendar()
	e = Event()




	e.name = "My cool event"
	e.begin = '2014-01-01 00:00:00'
	e.description = soup.find_all(_class="field--name-field-event-description")
	print(soup.find_all(_class="field--name-field-event-description").text)
	c.events.add(e)
	
	return c
	





if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Parse Events.rit.edu pages for calendar events')
	parser.add_argument('url',
						help='the url of the page to parse')
	parser.add_argument('--cachefile',
						help='the file to store the page HTML in, used for testing')

	args = parser.parse_args()

	fetch_html(args.url, cachefilename=args.cachefile)

	calendar = parse_html()

	with open('calendar.ics', 'w') as my_file:
		my_file.writelines(calendar.serialize_iter())

	# if cache was not user specified, remove it, it is temporary 
	if not args.cachefile:
		htmlfile.unlink()
