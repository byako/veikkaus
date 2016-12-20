#!/usr/bin/python

from __future__ import print_function
import sys
import json
import getopt
import os.path

GAMES = {"LOTTO":{"numbersLimit":40, "additionalLimit":40},"EJACKPOT":{"numbersLimit":50, "additionalLimit":10} }
COMMON_STATS = []
PRIMARY_STATS = []
ADDITIONAL_STATS = []

AVERAGE_STATS = 0
YEARS = [ "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016"]
QUIET = False
GAME = "unknown"

def print_usage():
    """Print usage manual"""
    print("\n Usage: ")
    print("-h prints this help")
    print("-q do not print out progress")
    sys.exit(0)

def setup():
    global GAMES
    global COMMON_STATS
    global PRIMARY_STATS
    global ADDITIONAL_STATS
    for i in range(0,GAMES[GAME]["numbersLimit"]):
        COMMON_STATS.append(0);
        PRIMARY_STATS.append(0);
    for i in range(0, GAMES[GAME]["additionalLimit"]):
        ADDITIONAL_STATS.append(0);

def process_results():
    """Count in numbers from draw round"""
    global AVERAGE_STATS
    global COMMON_STATS
    global PRIMARY_STATS
    global ADDITIONAL_STATS
    global GAMES
    global QUIET
    counter = 0;
    setup()
    for year in YEARS:
        for week in range(0, 54):
            filename = "results/" + GAME + "_" + str(year) + "_" + str(week) + ".json"
            plot_p_filename = "plot/" + GAME + "_" + str(year) + "_" + str(week).zfill(2) + "_p.data"
            plot_a_filename = "plot/" + GAME + "_" + str(year) + "_" + str(week).zfill(2) + "_a.data"
            plot_c_filename = "plot/" + GAME + "_" + str(year) + "_" + str(week).zfill(2) + "_c.data"
            plot_avg_filename = "plot/" + GAME + "_" + str(year) + "_" + str(week).zfill(2) + "_avg.data"
            if os.path.exists(filename):
                print("found file: " + filename) if QUIET == False else 0
                with open(filename) as json_file:
                    json_data = json.load(json_file)
                for draw in json_data["draws"]:
                    for result in draw["results"]:
                        for rprim in result["primary"]:
                            COMMON_STATS[int(rprim)-1] += 1
                            PRIMARY_STATS[int(rprim)-1] += 1
                        for rsec in result["secondary"]:
                            COMMON_STATS[int(rsec)-1] += 1
                            ADDITIONAL_STATS[int(rsec)-1] += 1
                tmpAvg = 0
                for tmpIdx in range(0,GAMES[GAME]["numbersLimit"]):
                    if GAME == "LOTTO":
                        tmpAvg += COMMON_STATS[tmpIdx]
                    elif GAME == "EJACKPOT":
                        tmpAvg += PRIMARY_STATS[tmpIdx]
            
                AVERAGE_STATS = tmpAvg / GAMES[GAME]["numbersLimit"]
                if os.path.exists(plot_p_filename) or os.path.exists(plot_p_filename) or\
                   os.path.exists(plot_p_filename or os.path.exists(plot_avg_filename)):
                    print("FOUND OUTPUT file. SKIPPING") if QUIET == False else 0
                    continue
                counter += 1
                save_to_file(plot_p_filename, plot_a_filename, plot_c_filename, plot_avg_filename)
    print("Total: " + str(counter))

def save_to_file(prim, addit, comm, avg):
    """Save counted values to corresponding file"""
    try:
        pf = open(prim, 'w')
        af = open(addit, 'w')
        cf = open(comm, 'w')
        avgf = open(avg, 'w')
        for num in range(1, GAMES[GAME]["numbersLimit"] + 1):
            pf.write(str(num) + "\t" + str(PRIMARY_STATS[num-1]) + "\n")
            if num <= GAMES[GAME]["additionalLimit"]:
                af.write(str(num) + "\t" + str(ADDITIONAL_STATS[num-1]) + "\n")
            cf.write(str(num) + "\t" + str(COMMON_STATS[num-1]) + "\n")
        avgf.write("1\t" + str(AVERAGE_STATS) + "\n" + str(GAMES[GAME]["numbersLimit"]) + "\t" + str(AVERAGE_STATS))
        pf.flush()
        af.flush()
        cf.flush()
        avgf.flush()
        pf.close()
        af.close()
        cf.close()
        avgf.close()
    except IOError, e:
        print('Could not open / write / save to file(s):' + str(e))

def parse_arguments(arguments):
    """Parse supported args"""
    global QUIET
    global GAME
    optlist, args = getopt.getopt(arguments, 'ha:qa:g:')
    for o, a in optlist:
        if o == '-h':
            print_usage()
        elif o == '-q':
            QUIET = True
        elif o == '-g':
            if a == 'lotto':
                GAME = 'LOTTO'
            elif a == 'ejackpot':
                GAME = 'EJACKPOT'

if __name__ == "__main__":
    parse_arguments(sys.argv[1:])
    if GAME != 'LOTTO' and GAME != 'EJACKPOT':
        print('ERROR: unsupported game: %s' % GAME)
        print('usage: %s [-q] -g <game>\n -g <game> Supported games: lotto, ejackpot\n -q quet mode' % sys.argv[0])
        exit(-1)
    process_results()
