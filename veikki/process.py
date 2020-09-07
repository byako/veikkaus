"""
Process all results, attempt forecast
"""

import json
import os.path
import getopt
import sys
import configparser
from random import randint
import numpy


def print_usage():
    """Print usage manual"""
    print("\n Usage: ")
    print("-h prints this help")
    print("-c <configfile>")
    sys.exit(0)


def parse_arguments(arguments, settings):
    """Get week number and year out of arguments"""
    optlist, args = getopt.getopt(arguments, "hqc:n:")
    if len(args) != 0:
        print("Unsupported parameters : %s" % args)
    for opt, arg in optlist:
        if opt == "-h":
            print_usage()
        elif opt == "-c":
            settings["config_file"] = arg
        elif opt == "-n":
            settings["iterations"] = int(arg)
        elif opt == "-q":
            settings["quiet"] = True
        else:
            print("ERROR: Unknown parameter %s" % opt)
            sys.exit(1)
    if settings["config_file"] == "":
        print_usage()


def parse_config(settings):
    """Save argument text to argument config_file file if it does not exist"""
    config = configparser.RawConfigParser()
    config.read(settings["config_file"])
    settings["majors"] = config.getint("Main", "majors")
    settings["lows"] = config.getint("Main", "mediums")
    settings["mediums"] = config.getint("Main", "lows")
    settings["bets"] = config.getint("Main", "bets")
    settings["adds_top"] = config.getint("Main", "adds_top")
    if settings["iterations"] == 0:
        new_iterations = config.getint("Main", "iterations")
        if new_iterations >= 1:
            settings["iterations"] = new_iterations
        else:
            print("ERROR: iterations in config file has to be >= 1")
            sys.exit(2)
    settings["quiet"] = config.getboolean("Main", "quiet")
    if (settings["majors"] + settings["mediums"] + settings["lows"]) > 5:
        print("Sum of parameters majors, mediums and lows cannot exceed 5")
        sys.exit(2)


def read_latest_results():
    """Read processed results"""
    text_contents = "{}"
    latest_file = "latest_EJACKPOT.json"
    latest_results = json.loads(text_contents)

    if not os.path.exists(latest_file):
        print("file does not exist: " + latest_file)
        return latest_results

    try:
        iff = open(latest_file, "r")
        text_contents = "[" + iff.read()[:-2] + "]"
        iff.close()
    except IOError as err:
        print(
            "Could not open / read from file :" + latest_file + ", error:" + err
        )
        iff.close()
        return latest_results

    latest_results = json.loads(text_contents)
    print("Found %d results" % len(latest_results))
    return latest_results


def find_duplicates(results):
    """See if there were any identical rounds"""
    longest_match = 0
    longest_match_infos = []
    longest_match_count = 0
    counts = {
        "d2_0_count": 0,
        "d2_1_count": 0,
        "d2_2_count": 0,
        "d3_0_count": 0,
        "d3_1_count": 0,
        "d3_2_count": 0,
        "d4_0_count": 0,
        "d4_1_count": 0,
        "d4_2_count": 0,
    }
    print("Looking for duplicates")
    for idx, res in enumerate(results):
        current_match = 0
        for idx2, res2 in enumerate(results[idx + 1 :]):
            print("%d / %d" % (idx, idx2), end="\r")
            if results[idx2]["numbers"] == res["numbers"]:
                print(
                    "\n%s %s %s / %s: %s / %s %s %s\n"
                    % (
                        res["year"],
                        res["week"],
                        res["numbers"],
                        res["adds"],
                        res2["numbers"],
                        res2["adds"],
                        res2["year"],
                        res2["week"],
                    )
                )
                current_match = 7
            else:
                matches = compare(
                    res["numbers"],
                    res["adds"],
                    res2["numbers"],
                    res2["adds"],
                )
                current_match = matches[0] + matches[1]
                if matches[0] == 2 and matches[1] == 0:
                    counts["d2_0_count"] += 1
                if matches[0] == 2 and matches[1] == 1:
                    counts["d2_1_count"] += 1
                if matches[0] == 2 and matches[1] == 2:
                    counts["d2_2_count"] += 1
                if matches[0] == 3 and matches[1] == 0:
                    counts["d3_0_count"] += 1
                if matches[0] == 3 and matches[1] == 1:
                    counts["d3_1_count"] += 1
                if matches[0] == 3 and matches[1] == 2:
                    counts["d3_2_count"] += 1
                if matches[0] == 4 and matches[1] == 0:
                    counts["d4_0_count"] += 1
                if matches[0] == 4 and matches[1] == 1:
                    counts["d4_1_count"] += 1
                if matches[0] == 4 and matches[1] == 2:
                    counts["d4_2_count"] += 1

            if current_match > longest_match:
                longest_match = current_match
                longest_match_count = 1
                longest_match_infos = []
                longest_match_infos.append(
                    (
                        res["year"],
                        res["week"],
                        res["numbers"],
                        res["adds"],
                        res2["numbers"],
                        res2["adds"],
                        res2["year"],
                        res2["week"],
                    )
                )
            elif current_match == longest_match:
                longest_match_count += 1
                longest_match_infos.append(
                    (
                        res["year"],
                        res["week"],
                        res["numbers"],
                        res["adds"],
                        res2["numbers"],
                        res2["adds"],
                        res2["year"],
                        res2["week"],
                    )
                )
    print(
        "\nDone looking for duplicates. Longest match: %d (%d)"
        % (longest_match, longest_match_count)
    )
    if len(longest_match_infos) < 10:
        for info in longest_match_infos:
            print(info)
    print("2:0 %d" % counts["d2_0_count"])
    print("2:1 %d" % counts["d2_1_count"])
    print("2:2 %d" % counts["d2_2_count"])
    print("3:0 %d" % counts["d3_0_count"])
    print("3:1 %d" % counts["d3_1_count"])
    print("3:2 %d" % counts["d3_2_count"])
    print("4:0 %d" % counts["d4_0_count"])
    print("4:1 %d" % counts["d4_1_count"])
    print("4:2 %d" % counts["d4_2_count"])


def compare(lista1, lista2, listb1, listb2):
    """get number of matches in two lists"""
    count1 = 0
    count2 = 0
    for i in lista1:
        if i in listb1:
            count1 += 1
    for i in lista2:
        if i in listb2:
            count2 += 1
    return (count1, count2)


def read_from_file(filename):
    """Save argument text to argument filename file if it does not exist"""
    text_contents = ""
    if not os.path.exists(filename):
        print("file does not exist: " + filename)
    else:
        try:
            iff = open(filename, "r")
            text_contents = iff.read()
            iff.close()
        except IOError as err:
            print(
                "Could not open / read from file :"
                + filename
                + ", error:"
                + err
            )
            iff.close()
    return text_contents


def get_money(mains, adds, year, week):
    """Get the match (e.g. 4 + 1) and the prize (e.g. 10350)"""
    response_text = read_from_file("results/EJACKPOT_%s_%s.json" % (year, week))
    if response_text != "":
        try:
            j = json.loads(response_text)
            for draw in j["draws"]:
                win_line = "%s" % mains
                if adds > 0:
                    win_line += "+%d" % adds
                win_line += " oikein"
                for prize in draw["prizeTiers"]:
                    if win_line == prize["name"]:
                        return "%8d.%02d" % (
                            prize["shareAmount"] / 100,
                            prize["shareAmount"] % 100,
                        )
        except:
            print("parsing of JSON round description failed")
            return -1
    print("WTF: %d/%d/%s/%s" % (mains, adds, year, week))
    return "       -.--"


def skip_repetition(results, mains, adds):
    """Do not allow more than three main numbers with any previous result"""
    matches = (0, 0)
    for idx in range(0, len(results)):
        matches = compare(
            results[idx]["numbers"], results[idx]["adds"], mains, adds
        )
    if (
        matches[0] > 3
        or (matches[0] == 3 and matches[1] > 0)
        or (matches[0] == 2 and matches[1] == 2)
    ):
        return True

    return False


def gen_random():
    """Just randomize the combination"""
    num1 = []
    num2 = []
    while len(num1) != 5:
        new_num1 = randint(1, 50)
        if new_num1 not in num1:
            num1.append(new_num1)
    num1.sort()
    while len(num2) != 2:
        new_num2 = randint(1, 10)
        if new_num2 not in num2:
            num2.append(new_num2)
    num2.sort()
    return (num1, num2)


def gen_stat(idx, data):
    """for current stats generate projection"""
    settings = data["settings"]
    results = data["results"]
    stat_debug = 0
    num1 = []
    num2 = []
    # here be dragons
    sorted_stat = numpy.argsort(results[idx]["stats_main"])
    if stat_debug:
        print(
            "stats_main(%d): %s\nsorted_stat: %s"
            % (len(sorted_stat), results[idx]["stats_main"], sorted_stat)
        )

    tops = sorted_stat[25:51]
    if stat_debug:
        print("tops:%s" % tops)
    mediums = sorted_stat[10:25]
    if stat_debug:
        print("mediums:%s" % mediums)
    lows = sorted_stat[1:10]
    if stat_debug:
        print("lows:%s" % lows)

    if len(tops) + len(mediums) + len(lows) != 50:
        print("WHAAAT?!")
        sys.exit(3)

    # gen majors
    while len(num1) < settings["majors"]:
        tops_idx = randint(0, len(tops) - 1)
        if tops[tops_idx] not in num1:
            num1.append(tops[tops_idx])
    # gen mediums
    while len(num1) < (settings["majors"] + settings["mediums"]):
        mediums_idx = randint(0, len(mediums) - 1)
        if mediums[mediums_idx] not in num1:
            num1.append(mediums[mediums_idx])
    # gen lows
    while len(num1) < 5:
        lows_idx = randint(0, len(lows) - 1)
        if lows[lows_idx] not in num1:
            num1.append(lows[lows_idx])

    stat_adds_sorted = numpy.argsort(results[idx]["stats_adds"])
    adds_top = stat_adds_sorted[-(settings["adds_top"]) :]
    if stat_debug:
        print(
            "idx %d, stat_adds_sorted: %s, stats_adds: %s"
            % (idx, stat_adds_sorted, results[idx]["stats_adds"])
        )
    while len(num2) < 2:
        adds_idx = randint(0, len(adds_top) - 1)
        if adds_top[adds_idx] not in num2:
            num2.append(adds_top[adds_idx])

    num1.sort()
    num2.sort()
    return (num1, num2)


def project(data):
    """ Randomize and see what happens """
    settings = data["settings"]
    results = data["results"]
    if settings["iterations"] > 1:
        settings["quiet"] = True
    rate_avg = 0
    # how many times go through all results (simulations number)
    for _ in range(0, settings["iterations"]):
        wins = 0
        income = 0
        rounds = 0
        skipped = 0
        if len(results) == 0:
            print("ERROR: no results")
            sys.exit(4)
        for idx in range(0, len(results) - 1):
            for _ in range(0, 1):
                rounds += 1
                # least accurate:
                # (num1, num2) = gen_random()
                # better
                skip = True
                while skip:
                    (num1, num2) = gen_stat(idx, data)
                    skip = skip_repetition(results, num1, num2)
                    if skip:
                        skipped += 1

                (nums, adds) = compare(
                    num1,
                    num2,
                    results[idx + 1]["numbers"],
                    results[idx + 1]["adds"],
                )
                if nums >= 2:
                    if nums == 2 and adds == 0:
                        continue
                    w_year = results[idx + 1]["year"]
                    w_week = results[idx + 1]["week"]
                    w_money = get_money(nums, adds, w_year, w_week)
                    income += float(w_money)
                    if not settings["quiet"]:
                        print(
                            "Win %d-%d %s/%2s : %20s %7s / %20s %7s %s"
                            % (
                                nums,
                                adds,
                                w_year,
                                w_week,
                                num1,
                                num2,
                                results[idx + 1]["numbers"],
                                results[idx + 1]["adds"],
                                w_money,
                            )
                        )
                    wins += 1
        print(
            "Rate: %3d / %d (%3.4f), - / +: %d / %7.2f, skipped %d"
            % (wins, rounds, wins / rounds, rounds * 2, income, skipped)
        )
        rate_avg += wins / rounds
    print("Rate_avg:        %3.4f" % (rate_avg / settings["iterations"]))


def stat_relative(data):
    """Assuming that stats were generated, show how popular numbers are drawn"""
    print("relative_stats:")
    for idx in range(10, len(data["results"])):
        relative_stats = []
        sorted_stat = numpy.argsort(
            data["results"][idx - 1]["stats_main"]
        ).tolist()
        # optionally - sort
        for num in data["results"][idx]["numbers"]:
            relative_stats.append(sorted_stat.index(num))
        relative_stats.sort()
        print(relative_stats)


def process(data):
    """Main logic"""
    print(data["settings"])
    data["results"] = read_latest_results()
    stats_main = []
    stats_adds = []
    for _ in range(0, 11):
        stats_adds.append(0)
    for _ in range(0, 51):
        stats_main.append(0)
    # populate stats per round
    for result in data["results"]:
        for num in result["numbers"]:
            stats_main[num] += 1
        result["stats_main"] = stats_main.copy()
        for num in result["adds"]:
            stats_adds[num] += 1
        # print(stats_adds)
        result["stats_adds"] = stats_adds.copy()
    # find_duplicates(data['results'])
    # project(data)
    stat_relative(data)
    sys.exit(0)


def starter(arguments):
    """Validate arguments and process results"""

    data = {
        "results": [],
        "settings": {
            "adds_top": 5,
            "majors": 2,
            "mediums": 2,
            "lows": 1,
            "bets": 1,
            "iterations": 0,
            "config_file": "",
            "quiet": True,
        },
    }

    parse_arguments(arguments, data["settings"])
    parse_config(data["settings"])
    process(data)
