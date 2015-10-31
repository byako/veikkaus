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

common_stats = [
0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0
];

primary_stats = [
0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0
];

additional_stats = [
0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0
];

average_stats = 0;

years = [ "2010", "2011", "2012", "2013", "2014", "2015" ]

def process_results():
    global average_stats;
    for year in years:
        for week in range(1, 54):
            filename = "results/lotto_" + str(year) + "_" + str(week) + ".json";
            plot_p_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_p.data";
            plot_a_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_a.data";
            plot_c_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_c.data";
            plot_avg_filename = "plot/" + str(year) + "_" + str(week).zfill(2) + "_avg.data";
            if os.path.exists(filename):
                print("found file: " + filename);
                if os.path.exists(plot_p_filename) or os.path.exists(plot_p_filename) or os.path.exists(plot_p_filename or os.path.exists(plot_avg_filename)):
                    print("FOUND OUTPUT file. SKIPPING");
                    continue;
                with open(filename) as json_file:
                    jsonData = json.load(json_file);
                for draw in jsonData["draws"]:
                    for result in draw["results"]:
                        for rprim in result["primary"]:
                            common_stats[int(rprim)-1] += 1;
                            primary_stats[int(rprim)-1] += 1;
                        for rsec in result["secondary"]:
                            common_stats[int(rsec)-1] += 1;
                            additional_stats[int(rsec)-1] += 1;
                tmpAvg = 0;
                for tmpIdx in range(0,38):
                    tmpAvg += common_stats[tmpIdx];
                average_stats = tmpAvg / 38;
                save_to_file(year, week, plot_p_filename, plot_a_filename, plot_c_filename, plot_avg_filename);

def save_to_file(year, week, prim, addit, comm, avg):
    try:
        pf = open(prim, 'w')
        af = open(addit, 'w')
        cf = open(comm, 'w')
        avgf = open(avg, 'w')
        for num in range(1, 39):
            pf.write(str(num) + "\t" + str(primary_stats[num-1]) + "\n");
            af.write(str(num) + "\t" + str(additional_stats[num-1]) + "\n");
            cf.write(str(num) + "\t" + str(common_stats[num-1]) + "\n");
        avgf.write("1\t" + str(average_stats) + "\n39\t" + str(average_stats));
        pf.flush()
        af.flush()
        cf.flush()
        avgf.flush()
        pf.close()
        af.close()
        cf.close()
        avgf.close()
    except IOError, e:
        print('Could not open / write / save to file(s):' + str(e));

if __name__ == "__main__":
    process_results()
