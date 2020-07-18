"""
Generate stat graphs and save to files
"""
import datetime
import getopt
import json
import logging
import os.path
import sys

logger = logging.getLogger("veikkilogger")
logger.setLevel(logging.DEBUG)

CONFIG = {"numbersLimit": 50, "additionalLimit": 10}
COMMON_STATS = [0] * CONFIG["numbersLimit"]
PRIMARY_STATS = [0] * CONFIG["numbersLimit"]
ADDITIONAL_STATS = [0] * CONFIG["additionalLimit"]

AVERAGE_STATS = 0


def gen_plot_source(_=None):
    """Count in numbers from draw round"""
    counter = 0
    for year in range(2009, datetime.datetime.now().year + 1):
        for week in range(0, 54):
            filename = f"results/ejackpot_{year}_{week}.json"
            plot_p_filename = f"plot/ejackpot_{year}_{week:02}_p.data"
            plot_a_filename = f"plot/ejackpot_{year}_{week:02}_a.data"
            plot_c_filename = f"plot/ejackpot_{year}_{week:02}_c.data"
            plot_avg_filename = f"plot/ejackpot_{year}_{week:02}_avg.data"
            if os.path.exists(filename):
                logger.debug("found file: %s", filename)
                with open(filename) as json_file:
                    draw = json.load(json_file)[0]
                    for rprim in draw["results"][0]["primary"]:
                        COMMON_STATS[int(rprim) - 1] += 1
                        PRIMARY_STATS[int(rprim) - 1] += 1
                    for rsec in draw["results"][0]["secondary"]:
                        COMMON_STATS[int(rsec) - 1] += 1
                        ADDITIONAL_STATS[int(rsec) - 1] += 1
                tmpAvg = 0
                for tmpIdx in range(0, CONFIG["numbersLimit"]):
                    tmpAvg += PRIMARY_STATS[tmpIdx]

                AVERAGE_STATS = tmpAvg / CONFIG["numbersLimit"]
                if any(
                    os.path.exists(plot_p_filename),
                    os.path.exists(plot_a_filename),
                    os.path.exists(plot_c_filename),
                    os.path.exists(plot_avg_filename),
                ):
                    logger.debug("FOUND OUTPUT file. SKIPPING")
                    continue
                counter += 1
                save_to_file(
                    plot_p_filename,
                    plot_a_filename,
                    plot_c_filename,
                    plot_avg_filename,
                )
    logger.debug("Total: %s", counter)


def save_to_file(prim, addit, comm, avg):
    """Save counted values to corresponding file"""
    try:
        pf = open(prim, "w")
        af = open(addit, "w")
        cf = open(comm, "w")
        avgf = open(avg, "w")
        for num in range(1, CONFIG["numbersLimit"] + 1):
            pf.write(f"{num}\t{PRIMARY_STATS[num - 1]}\n")
            if num <= CONFIG["additionalLimit"]:
                af.write(f"{num}\t{ADDITIONAL_STATS[num - 1]}\n")
            cf.write(f"{num}\t{COMMON_STATS[num - 1]}\n")
        avgf.write(
            f'1\t{AVERAGE_STATS}\n{CONFIG["numbersLimit"]}\t{AVERAGE_STATS}'
        )
        pf.flush()
        af.flush()
        cf.flush()
        avgf.flush()
        pf.close()
        af.close()
        cf.close()
        avgf.close()
    except IOError as err:
        logger.error("File I/O error:%s", err)
