#!/usr/bin/python

from __future__ import print_function
import sys
import json
import getopt
import os.path

COMMON_STATS = [
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

PRIMARY_STATS = [
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

ADDITIONAL_STATS = [
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

AVERAGE_STATS = 0
YEARS = [ "2010", "2011", "2012", "2013", "2014", "2015"]
QUIET = False

def print_usage():
    """Print usage manual"""
    print("\n Usage: ")
    print("-h prints this help")
    print("-q do not print out progress")
    sys.exit(0)

def process_results():
    """Count in numbers from draw round"""
    global AVERAGE_STATS
    global QUIET
    counter = 0;
    for year in YEARS:
        for week in range(1, 54):
            filename = "results/lotto_" + str(year) + "_" + str(week) + ".json"
            plot_p_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_p.data"
            plot_a_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_a.data"
            plot_c_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_c.data"
            plot_avg_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_avg.data"
            if os.path.exists(filename):
                print("found file: " + filename) if QUIET == False else 0
                with open(filename) as json_file:
                    jsonData = json.load(json_file)
                for draw in jsonData["draws"]:
                    for result in draw["results"]:
                        for rprim in result["primary"]:
                            COMMON_STATS[int(rprim)-1] += 1
                            PRIMARY_STATS[int(rprim)-1] += 1
                        for rsec in result["secondary"]:
                            COMMON_STATS[int(rsec)-1] += 1
                            ADDITIONAL_STATS[int(rsec)-1] += 1
                tmpAvg = 0
                for tmpIdx in range(0,38):
                    tmpAvg += COMMON_STATS[tmpIdx]
                AVERAGE_STATS = tmpAvg / 38
                if os.path.exists(plot_p_filename) or os.path.exists(plot_p_filename) or\
                   os.path.exists(plot_p_filename or os.path.exists(plot_avg_filename)):
                    print("FOUND OUTPUT file. SKIPPING") if QUIET == False else 0
                    continue
                counter += 1
                save_to_file(plot_p_filename, plot_a_filename, plot_c_filename, plot_avg_filename)
    print("Total: " + str(counter)) if QUIET == False else 0

def save_to_file(prim, addit, comm, avg):
    """Save counted values to corresponding file"""
    try:
        pf = open(prim, 'w')
        af = open(addit, 'w')
        cf = open(comm, 'w')
        avgf = open(avg, 'w')
        for num in range(1, 39):
            pf.write(str(num) + "\t" + str(PRIMARY_STATS[num-1]) + "\n")
            af.write(str(num) + "\t" + str(ADDITIONAL_STATS[num-1]) + "\n")
            cf.write(str(num) + "\t" + str(COMMON_STATS[num-1]) + "\n")
        avgf.write("1\t" + str(AVERAGE_STATS) + "\n39\t" + str(AVERAGE_STATS))
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
    optlist, args = getopt.getopt(arguments, 'ha:qa:')
    for o, a in optlist:
        if o == '-h':
            print_usage()
        elif o == '-q':
            QUIET = True

if __name__ == "__main__":
    parse_arguments(sys.argv[1:])
    process_results()
