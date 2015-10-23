#!/usr/bin/python

from __future__ import print_function
import sys
import requests
import json
import copy
import time
import datetime
import getopt
import os.path


# the veikkaus site address
host="https://www.veikkaus.fi"
latest_file='latest.txt'

# required headers
headers = {
	'Content-type':'application/json',
	'Accept':'application/json',
	'X-ESA-APi-Key':'ROBOT'
}

def login (username, password): 
	s = requests.Session()
	login_req = {"type":"STANDARD_LOGIN","login":username,"password":password}
	r = s.post(host + "/api/v1/sessions", verify=True, data=json.dumps(login_req), headers=headers)
	if r.status_code == 200:
		return s
	else:
		raise Exception("Authentication failed", r.status_code)

def print_usage():
	print("\n Usage: ");
	print("-h prints this help")
	print("-u <username>")
	print("-p <password>")
	print("-w <week number[1..53]>")
	print("-y <year number[2010..$CurYear>")
	sys.exit(0)

def append_to_latest(text):
	if os.path.exists(latest_file):
		try:
			print('appending to ' + latest_file + ' : ' + text)
			of = open(latest_file, 'a')
			of.write(text + '\n')
			of.flush()
			of.close();
		except IOError, e:
			print('Failed to append. Error: ' + e)
	else:
		print('could not find latest file: ' + latest_file)

def save_to_file(filename, text):
	if os.path.exists(filename):
		print("file already exists: " + filename)
	else:
		try:
			print('saving to file ' + filename)
			of = open(filename, 'w')
			of.write(text)
			of.flush()
			of.close()
		except IOError, e:
			print('Could not open / write / save to file :' + filename + ' , error:' + e);

def parse_arguments ( arguments ):
	optlist, args = getopt.getopt(arguments, 'ha:u:p:w:y:')
	params = {
		"username":"",
		"passowrd":"",
		"year":"1970",
		"week":"54"
	}
	for o, a in optlist:
		if o == '-h':
			print_usage();
		elif o == '-u':
			params["username"] = a
		elif o == '-p':
			params["password"] = a
		elif o == '-y':
			params["year"] = a
		elif o == '-w':
			params["week"] = a
	return params
	
def get_draw ( params ):
	yearN1 = int(params["year"])
	weekN1 = int(params["week"])
	lastWeek = datetime.date(yearN1, 12, 27).isocalendar()[1]
	if weekN1 > lastWeek:
		print('Year %d had only %d weeks' % (yearN1, lastWeek))
		return
	elif weekN1 == lastWeek:
		yearN2 = yearN1 + 1
		weekN2 = 1
	else:
		yearN2 = yearN1
		weekN2 = weekN1 + 1
	weekStart = "%.0f000" % time.mktime(time.strptime("%d %d 1 0 0" % (yearN1, weekN1), "%Y %W %w %H %M"));
	weekEnd   = "%.0f000" % time.mktime(time.strptime("%d %d 1 0 0" % (yearN2, weekN2), "%Y %W %w %H %M"));
	r = requests.get(host + "/api/v1/draw-games/draws?game-names=LOTTO&status=RESULTS_AVAILABLE&date-from=%s&date-to=%s" % (weekStart, weekEnd), verify=True, headers=headers)
	if r.status_code == 200:
		try:
			j = r.json();
			for draw in j["draws"]:
				print("game: %s, index: %s, draw: %s, status: %s" % (draw["gameName"],draw["brandName"],draw["id"],draw["status"]))
				latest_result = '' + params["year"] + ',' + params["week"] + '-1,' + "01.01" + ", ";
				# 2014,52-1,27.12., 5  11  16  17  22  24  26  ,+, 1  32
				for result in draw["results"]:
					print("result:\t", end='');
					for rprim in result["primary"]:
						print("%2s " % rprim, end='');
						latest_result = latest_result + rprim + "  "
					print(' + ', end='');
					latest_result += ',+, '
					for rsec in result["secondary"]:
						print("%2s " % rsec, end='');
						latest_result = latest_result + rsec + "  "
					print('');
				print('');
				for prize in draw["prizeTiers"]:
					print("%6d : %10d : %10s" % (prize["shareCount"], prize["shareAmount"], prize["name"]), end='');
					if prize["multiplier"] == True:
						print(" : x2", end='');
					print('');
			save_to_file('results/lotto_' + params["year"] + '_' + params["week"] + '.json', r.text);
			append_to_latest(latest_result);
		except: 
			print("request failed")
	else:
		print("request failed: " + r.text)


def robot( arguments ): 
	params = parse_arguments( arguments )
	if params["username"] == "" or params["password"] == "" or params["week"] == "54" or params["year"] == "1970":
		print_usage();
	elif int(params["year"]) < 2010:
		print("oldest results are from 2010")
	elif int(params["year"]) > datetime.datetime.now().year:
		print("You want results from future? I don't think so.");
	elif int(params["week"]) < 1 or int(params["week"]) > 53:
		print("Wrong week number");
	elif params["year"] == str(datetime.datetime.now().year) and int(params["week"]) > datetime.datetime.now().isocalendar()[1]:
		print("Week number is too big for this year");
	else:
		print("Fetching results for %s / %s" % (params["year"], params["week"]));
		get_draw(params);
		sys.exit(0);
	print_usage();

if __name__ == "__main__":
	robot(sys.argv[1:])
