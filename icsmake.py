from ics import Calendar, Event
from bs4 import BeautifulSoup
import argparse
import requests
from pathlib import Path
from dateutil import parser as dateparser



def fetch_html(url, cachefilename="event.html"):
	htmlfile = Path(cachefilename)

	if not htmlfile.exists():
		
		response = requests.get(url)
		with htmlfile.open("w") as f:
			f.write(response.text)

def parse_html(cachefilename="event.html"):
	htmlfile = Path(cachefilename)
	html = htmlfile.read_text()
	soup = BeautifulSoup(html, features="html.parser")

	c = Calendar()

	# parse details that are the same for every event
	name = soup.find(attrs={'class': "field--name-title"}).get_text().strip()
	description = soup.find(attrs={'class': "field--name-field-event-description"}).get_text().strip()

	for event_html in soup.find_all(attrs={'class': "paragraph--type--event-schedule"}):

		
		e = Event()
		e.name = name
		e.description = description

		items = list(event_html.find_all("div"))
		# # debug
		# for i in range(len(items)):
		# 	txt = items[i].get_text()
		# 	txt = txt.strip()
		# 	if txt != "":
		# 		print(i, txt)

		date = items[0].get_text()
		timerange = items[1].get_text()
		timerange = timerange.split("-")

		starttime = date + " " + timerange[0]
		endtime = date + " " + timerange[1]

		e.begin = dateparser.parse(starttime)
		e.end = dateparser.parse(endtime)

		location = items[2].get_text()
		room = items[3].get_text()
		room = room.split(":")[1].strip()
		location = location.strip() + " - " + room
		
		e.location = location

		c.events.add(e)
		
	return c
	





if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Parse Events.rit.edu pages for calendar events')
	parser.add_argument('url',
						help='the url of the page to parse')
	parser.add_argument('--cachefile',
						help='the file to store the page HTML in, used for testing')

	args = parser.parse_args()

	if args.cachefile:
		fetch_html(args.url, cachefilename=args.cachefile)

		calendar = parse_html(cachefilename=args.cachefile)

	else:
		fetch_html(args.url)

		calendar = parse_html()

	with open('calendar.ics', 'w') as my_file:
		my_file.writelines(calendar.serialize_iter())

	# if cache was not user specified, remove it, it is temporary 
	if args.cachefile:
		htmlfile.unlink()
