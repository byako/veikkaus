#!/usr/bin/python

from __future__ import print_function
import sys
import json
import time
import glob
import datetime
import getopt
import os.path
import subprocess

def print_usage():
    """Print usage manual"""
    print("\n Usage: ")
    print('[-r|--regenerate] re-generate latest_$GAME.json file from results/*json')
    print("-h prints this help")
    print('-g <game>')
    print("-w <week number[1..53]>")
    print("-y <year number[2010..$CurYear]>")
    sys.exit(0)

def parse_arguments(arguments):
    """Get week number and year out of arguments"""
    optlist, args = getopt.getopt(arguments, 'ha:w:y:g:r')
    params = {
        "regenerate":False,
        "year":"1970",
        "week":"54",
        "game":"unknown"
    }
    for o, a in optlist:
        if o == '-h':
            print_usage()
        elif o == '-y':
            params["year"] = a
        elif o == '-w':
            params["week"] = a
        elif o == '-r':
            params["regenerate"] = True
        elif o == '-g':
            if a == "lotto":
                params["game"] = "LOTTO"
            elif a == "ejackpot":
                params["game"] = "EJACKPOT"
    return params

def read_from_file(filename):
    """Save argument text to argument filename file if it does not exist"""
    text_contents = ""
    print('reading from file ' + filename)
    if not os.path.exists(filename):
        print("file does not exist: " + filename)
        return text_contents
    else:
        try:
            iff = open(filename, 'r')
            text_contents = iff.read()
            iff.close()
        except IOError, e:
            print('Could not open / read from file :' + filename + ', error:' + e)
            iff.close()
            return text_contents
        return text_contents

def print_draw(params):
    """Fetch draw result from VEIKKAUS_HOST"""
    yearN1 = int(params["year"])
    weekN1 = int(params["week"])
    lastWeek = datetime.date(yearN1, 12, 28).isocalendar()[1] - 1
    if weekN1 > lastWeek:
        print('Year %d had only %d weeks' % (yearN1, lastWeek))
        return
    elif weekN1 == lastWeek:
        yearN2 = yearN1 + 1
        weekN2 = 0
    else:
        yearN2 = yearN1
        weekN2 = weekN1 + 1
    weekStart = "%.0f000" % time.mktime(time.strptime("%d %d 1 0 0" % (yearN1, weekN1),
                                                      "%Y %W %w %H %M"))
    weekEnd = "%.0f000" % time.mktime(time.strptime("%d %d 1 0 0" % (yearN2, weekN2),
                                                    "%Y %W %w %H %M"))
    print("Parsing results for %s / %s : %s / %s" % (params["year"], params["week"], weekStart, weekEnd))

    responseText = read_from_file('results/' + params["game"] + '_' + params["year"] + '_' + params["week"] +'.json')
    if responseText != "":
        try:
            j = json.loads(responseText)
            for draw in j["draws"]:
                latest_result = json.loads("{\"year\":1970,\"week\":1,\"numbers\":[],\"adds\":[],\"date\":\"01.01\"}")
                drawTime = time.localtime(draw["drawTime"] / 1000)
                latest_result["year"] = str(yearN1)
                latest_result["week"] = str(weekN1)
                latest_result["date"] = time.strftime("%m.%d", drawTime)
                for prim in draw["results"][0]["primary"]:
                    latest_result["numbers"].append(int(prim))
                for addit in draw["results"][0]["secondary"]:
                    latest_result["adds"].append(int(addit))
                print("game: %s, index: %s, draw: %s (%s / %s.%s)" %
                      (draw["gameName"], draw["brandName"], draw["id"],
                      latest_result["week"], latest_result["year"], latest_result["date"]))
                print(" %s / %s" % (json.dumps(latest_result["numbers"]), json.dumps(latest_result["adds"])))
                for prize in draw["prizeTiers"]:
                    print("%6d : %8d.%02d : %10s" % (prize["shareCount"],
                                                     prize["shareAmount"] / 100,
                                                     prize["shareAmount"] % 100,
                                                     prize["name"]), end='')
                    if params["game"] == "LOTTO":
                        if prize["multiplier"] == True:
                            print(" : x2", end='')
                    print('')
        except:
            print("parsing of JSON round description failed")
            return -1
    else:
        print("could not read from file properly: " + responseText)
        return -2

    return 0

def regenerate(params):
    """read through results/ folder and generate new latest_$GAME file """
    files = subprocess.check_output("ls -l", stderr=subprocess.STDOUT, shell=False);
    print("re-generating latest_%s.json" % params["game"])
    files = files.split("\n")
    print("got %d files" % len(files))
    for filename in files:
        print(filename)
    return 0

def starter(arguments):
    """Validate arguments and process results"""
    do_print_usage = False
    RC = 0

    params = parse_arguments(arguments)
    if params["regenerate"] == False:
        if params["week"] == "54" or params["year"] == "1970":
            do_print_usage = True
        elif int(params["year"]) < 2009:
            print("oldest results are from 2009")
            do_print_usage = True
        elif int(params["year"]) > datetime.datetime.now().year:
            print("You want results from future? I don't think so.")
            do_print_usage = True
        elif int(params["week"]) < 0 or int(params["week"]) > 53:
            print("Wrong week number")
            do_print_usage = True
        elif params["year"] == str(datetime.datetime.now().year) and int(params["week"]) > \
                               datetime.datetime.now().isocalendar()[1]:
            print("Week number is too big for this year")
            do_print_usage = True

    if params["game"] != "EJACKPOT" and params["game"] != "LOTTO":
        print("Supported games: ejackpot, lotto")
        do_print_usage = True

    if do_print_usage == True:
        print_usage()
        sys.exit(1)

    if params["regenerate"] == True:
        RC = regenerate(params)
    else:
        RC = print_draw(params)

    sys.exit(RC)

if __name__ == "__main__":
    starter(sys.argv[1:])
