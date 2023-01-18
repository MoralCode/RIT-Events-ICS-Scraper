from ics import Calendar, Event
from bs4 import BeautifulSoup
import argparse
import requests
from pathlib import Path
from dateutil import parser as dateparser
from pytz import timezone
import pytz



def fetch_html(url, cachefilename="event.html"):
	htmlfile = Path(cachefilename)

	if not htmlfile.exists():
		
		response = requests.get(url)
		with htmlfile.open("w") as f:
			f.write(response.text)

def parse_html(cachefilename="event.html", exclude_before=None, tz=""):

	exclude_before = dateparser.parse(exclude_before) if exclude_before is not None else None
	htmlfile = Path(cachefilename)
	html = htmlfile.read_text()
	soup = BeautifulSoup(html, features="html.parser")

	c = Calendar()

	# parse details that are the same for every event
	name = soup.find(attrs={'class': "field--name-title"}).get_text().strip()
	description = soup.find(attrs={'class': "field--name-field-event-description"}).get_text().strip()
	tz = timezone(tz)

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

		starttime = dateparser.parse(starttime)
		print("processing event starting at:", starttime)
		endtime = dateparser.parse(endtime)
		e.begin = tz.localize(starttime)
		e.end = tz.localize(endtime)

		location = items[2].get_text()
		room = items[3].get_text()
		room = room.split(":")[1].strip()
		location = location.strip() + " - " + room
		
		e.location = location
		print(e.begin)
		print(starttime)
		print(exclude_before)
		if exclude_before and starttime > exclude_before:
			c.events.add(e)
		else:
			print("\texcluded due to date filter")
		
	return c
	





if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Parse Events.rit.edu pages for calendar events')
	parser.add_argument('url',
						help='the url of the page to parse')
	parser.add_argument('--cachefile',
						help='the file to store the page HTML in, used for testing')
	parser.add_argument('--exclude-before',
						help='exclude events happening before a certain date. Example: "2023-01-01"')
	parser.add_argument("--timezone", default="US/Eastern", help="the timezone to use if none is available in the source")
	parser.add_argument('--output', default="calendar.ics",
						help='the filename to store the ics file in')
	args = parser.parse_args()

	if args.cachefile:
		fetch_html(args.url, cachefilename=args.cachefile)

		calendar = parse_html(cachefilename=args.cachefile)

	else:
		fetch_html(args.url)

		calendar = parse_html(exclude_before=args.exclude_before, tz=args.timezone)

	with open(args.output, 'w') as my_file:
		my_file.writelines(calendar.serialize_iter())

	# if cache was not user specified, remove it, it is temporary 
	if args.cachefile:
		htmlfile.unlink()
