"""
Process all results, attempt forecast
"""

import logging
import sys
import configparser
from random import randint
import multiprocessing
import numpy
from statistics import geometric_mean, mean 

from handies import load_draws_from_file, load_latest_file
from plot_results import plot_history

logger = logging.getLogger("veikkilogger")


def print_usage():
    """Print usage manual"""
    print(
        """
Usage:
-h prints this help
-c <configfile>
"""
    )
    sys.exit(0)


def parse_config(params: dict) -> None:
    """
    Load and parse config file
    """
    config = configparser.RawConfigParser()
    config.read(params["config"])
    settings = params["settings"]
    settings["majors"] = config.getint("Main", "majors")
    settings["lows"] = config.getint("Main", "mediums")
    settings["mediums"] = config.getint("Main", "lows")
    settings["majors_length"] = config.getint("Main", "majors_length")
    settings["lows_length"] = config.getint("Main", "mediums_length")
    settings["mediums_length"] = config.getint("Main", "lows_length")
    settings["bets"] = config.getint("Main", "bets")
    settings["adds_top"] = config.getint("Main", "adds_top")
    if params["iterations"] == 0:
        new_iterations = config.getint("Main", "iterations")
        if new_iterations >= 1:
            params["iterations"] = new_iterations
        else:
            logger.error("ERROR: iterations in config file has to be >= 1")
            sys.exit(1)
    if (settings["majors"] + settings["mediums"] + settings["lows"]) > 5:
        logger.error(
            "Sum of parameters majors, mediums and lows cannot exceed 5"
        )
        sys.exit(2)

    logger.debug("settings:")
    for params_key in params["settings"]:
        logger.debug("\t%s: %s", params_key, params["settings"][params_key])


def find_duplicates(results: list) -> None:
    """
    Find how many numbers in primary and adds occured in multiple draws, e.g.
    '3:1: 166' means 166 times at least two draws had 3 primary numbers and 1
    additional number the same
    """
    longest_match = 0
    longest_match_infos = []
    longest_match_count = 0
    counts = {
        "2:0": 0,
        "2:1": 0,
        "2:2": 0,
        "3:0": 0,
        "3:1": 0,
        "3:2": 0,
        "4:0": 0,
        "4:1": 0,
        "4:2": 0,
        "5:0": 0,
        "5:1": 0,
        "5:2": 0,
    }
    print("Looking for duplicates")
    for idx, res in enumerate(results):
        current_match = 0
        for idx2, res2 in enumerate(results[(idx + 1) :]):
#            if res2["primary"] == res["primary"]:
#                print("%d / %d" % (idx, idx2), end="\r")
#                print(
#                    "\n%s %s %s / %s: %s / %s %s %s\n"
#                    % (
#                        res["year"],
#                        res["week"],
#                        res["primary"],
#                        res["adds"],
#                        res2["primary"],
#                        res2["adds"],
#                        res2["year"],
#                        res2["week"],
#                    )
#                )
#                current_match = 7
#            else:
            matches = compare(
                res["primary"],
                res["adds"],
                res2["primary"],
                res2["adds"],
            )
            current_match = matches[0] + matches[1]
            if matches[0] > 1:
                match = "%d:%d" % (matches[0], matches[1])
                if not match.startswith("0:"):
                    counts[match] += 1
                    if match.startswith("4"):
                        print("%s: %s/%s - %s/%s : %s-%s - %s-%s" % (
                            match, res["year"], res["week"], res2["year"], res2["week"], res["primary"], res["adds"], res2["primary"], res2["adds"]))

            if current_match > longest_match:
                longest_match = current_match
                longest_match_count = 1
                longest_match_infos.append(
                    (
                        res["year"],
                        res["week"],
                        res["primary"],
                        res["adds"],
                        res2["primary"],
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
                        res["primary"],
                        res["adds"],
                        res2["primary"],
                        res2["adds"],
                        res2["year"],
                        res2["week"],
                    )
                )
    print(
        "Done looking for duplicates. Longest match: %d (%d)"
        % (longest_match, longest_match_count)
    )
#    if len(longest_match_infos) < 10:
#        for info in longest_match_infos:
#            print(info)
    for count_key in counts:
        logger.debug("%s %d", count_key, counts[count_key])


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


def get_money(mains, adds, year, week):
    """Get the match (e.g. 4 + 1) and the prize (e.g. 10350)"""
    draws = load_draws_from_file({"year": year, "week": week, "quiet": True})
    if not draws:
        return 0
    win_line = "%s" % mains
    # since 2017/04 '+0' is added to prize name
    if adds != 0 or int(year) > 2017 or (int(year) == 2017 and int(week) > 3):
        win_line += "+%d" % adds
    win_line += " oikein"
    for prize in draws[0]["scores"]:
        if win_line == prize["name"]:
            return "%8d.%02d" % (
                prize["shareAmount"] / 100,
                prize["shareAmount"] % 100,
            )
    logger.debug("WTF: %d/%d/%s/%s", mains, adds, year, week)
    return "0"


def skip_repetition(results, mains, adds):
    """
    Do not allow more than three main numbers with any previous result
    """
    matches = (0, 0)
    for res in results:
        matches = compare(res["primary"], res["adds"], mains, adds)
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


def gen_stat(idx, params):  # pylint: disable=too-many-locals
    """for current stats generate projection"""
    settings = params["settings"]
    results = params["results"]
    num1 = []
    num2 = []

    sorted_stat = numpy.argsort(results[idx]["stats_main"])
    if not params["quiet"]:
        print(
            "stats_main(%d): %s\nsorted_stat: %s"
            % (len(sorted_stat), results[idx]["stats_main"], sorted_stat)
        )

    tops = sorted_stat[(50 - params["settings"]["majors_length"]) : 51]
    mediums = sorted_stat[
        params["settings"]["lows_length"] : (
            50 - params["settings"]["majors_length"]
        )
    ]
    lows = sorted_stat[1 : params["settings"]["lows_length"]]
    if not params["quiet"]:
        print("tops:%s" % tops)
        print("mediums:%s" % mediums)
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
    if not params["quiet"]:
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


def project(params):
    """parallel project"""
    cpus = params["iterations"]
    # how many times go through all results (simulations number)
    with multiprocessing.Pool(multiprocessing.cpu_count()) as plot_pool:
        plot_pool.map(project_once, [params] * params["iterations"])


def project_once(params):  # pylint: disable=too-many-locals
    """Randomize and see what happens"""
    results = params["results"]
    rate_avg = 0

    wins = 0
    income = 0
    rounds = 0
    skipped = 0
    if len(results) == 0:
        print("ERROR: no results")
        sys.exit(4)
    for idx in range(0, len(results) - 1):
        for _ in range(0, params["settings"]["bets"]):
            rounds += 1
            # least accurate:
            # (num1, num2) = gen_random()
            # better
            skip = True
            while skip:
                (num1, num2) = gen_stat(idx, params)
                skip = skip_repetition(results, num1, num2)
                if skip:
                    skipped += 1

            (nums, adds) = compare(
                num1,
                num2,
                results[idx + 1]["primary"],
                results[idx + 1]["adds"],
            )
            if nums >= 2:  # try matched 2 or more primary, get prize
                if nums == 2 and adds == 0:  # 2+0 wins nothing, skip
                    continue
                w_year = results[idx + 1]["year"]
                w_week = results[idx + 1]["week"]
                w_money = get_money(nums, adds, w_year, w_week)
                income += float(w_money)
                if float(w_money) > 50:
                    print(
                        "Win %d-%d %s/%2s : %20s %7s / %20s %7s %s"
                        % (
                            nums,
                            adds,
                            w_year,
                            w_week,
                            num1,
                            num2,
                            results[idx + 1]["primary"],
                            results[idx + 1]["adds"],
                            w_money,
                        )
                    )
                wins += 1

    rate_avg += wins / rounds
    print(
        "Wins: %3d / Rounds %4d (Rate %3.4f), - / +: %4d / %7.2f, "
        "skipped %04d | rate: %3.4f"
        % (wins, rounds, wins / rounds, rounds * 2, income, skipped, rate_avg)
    )


def stat_relative(params):
    """
    Assuming that stats were generated, show how popular numbers are drawn
    """
    print("relative_stats:")
    all_relative_stats = []
    all_means = []
    all_means_avg = []
    all_geomeans = []
    all_geomeans_avg = []
    for idx in range(10, len(params["results"])):
        relative_stats = []
        sorted_stat = numpy.argsort(
            params["results"][idx - 1]["stats_main"]
        ).tolist()
        # optionally - sort
        for num in params["results"][idx]["primary"]:
            relative_stats.append(sorted_stat.index(num))
        relative_stats.sort()
        all_relative_stats.append(relative_stats)

        all_means.append(mean(relative_stats))
        all_means_avg.append(mean(all_means))

        all_geomeans.append(geometric_mean(relative_stats))
        all_geomeans_avg.append(geometric_mean(all_geomeans))

        #print(relative_stats)
    plot_history(all_means, all_means_avg, "/tmp/means.png")
    plot_history(all_geomeans, all_geomeans_avg, "/tmp/geomeans.png")
    print("Done plotting relative stats")
    print("/tmp/means.png /tmp/geomeans.png")


def _prepare_to_process(params):
    """
    Populate config, results, stats per game round
    """
    params.update(
        {
            "results": [],
            "settings": {
                "adds_top": 5,
                "majors": 2,
                "mediums": 2,
                "lows": 1,
                "bets": 1,
                "quiet": True,
            },
        }
    )

    parse_config(params)

    params["results"] = load_latest_file(params)
    stats_main = []
    stats_adds = []
    for _ in range(0, 13):
        stats_adds.append(0)
    for _ in range(0, 51):
        stats_main.append(0)
    # populate stats per round
    for result in params["results"]:
        for num in result["primary"]:
            stats_main[num] += 1
        result["stats_main"] = stats_main.copy()
        for num in result["adds"]:
            stats_adds[num] += 1
        # print(stats_adds)
        result["stats_adds"] = stats_adds.copy()


def do_process(params):
    """
    Setup and call processing
    """
    _prepare_to_process(params)
    # find_duplicates(params["results"])
    project(params)
    # stat_relative(params)


def process_optimize(params):
    """
    Bruteforce parameters to increase winnig rate
    """
    _prepare_to_process(params)
    for majors in range(0, 6):
        for mediums in range(0, 6 - majors):
            for lows in range(0, 6 - majors - mediums):
                params["settings"].update(
                    {
                        "majors": majors,
                        "mediums": mediums,
                        "lows": lows,
                    }
                )
                print()
                print(params["settings"])
                project(params)
