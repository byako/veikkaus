"""
Main starting point
"""

import argparse
import datetime
import logging
import os
import sys

from handies import load_and_print_draw, print_latest_result_date
from fetch_results import get_week_results
from plot_results import plot_all
from processing import do_process, process_optimize
from regenerate import refetch_all, regenerate_latest


logger = logging.getLogger("veikkilogger")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)
logger.setLevel(logging.INFO)

params = {
    "year": None,
    "week": None,
    "commands": [],
    "latest_file": "latest_ejackpot.json",
    "config": "config.ini",
    "iterations": 0,
    "quiet": False,
    "debug": True,
}


commands = {
    "fetch": get_week_results,
    "latest": print_latest_result_date,
    "parse": load_and_print_draw,
    "plot": plot_all,
    "process": do_process,
    "optimize": process_optimize,
    "refetch": refetch_all,
    "regen": regenerate_latest,
}


def sanitize(parameters):
    """
    Check params properties sanitiy
    """
    if parameters["week"] is None or parameters["year"] is None:
        if set(parameters["commands"]).intersection({"parse", "fetch"}):
            logger.error("week and year are required for fetch and parse")
        else:
            return
    elif not datetime.datetime.now().year >= parameters["year"] >= 2009:
        logger.error("Years supported: 2009..now")
    elif not 54 >= parameters["week"] >= 0:
        logger.error("Wrong week number")
    else:
        return

    sys.exit(1)


argParser = argparse.ArgumentParser("python3 veikki")
argParser.add_argument(
    "-q", "--quiet", action="store_true", help="Suppress output"
)
argParser.add_argument("-d", "--debug", action="store_true", help="Super verbose")
argParser.add_argument("-w", "--week")
argParser.add_argument("-y", "--year")
argParser.add_argument("-i", "--iterations")
argParser.add_argument("-c", "--config")
argParser.add_argument(
    "command",
    nargs="+",
    help="latest, parse, plot, process, refetch, regen",
)

args = argParser.parse_args()

params["commands"] = args.command
if args.iterations:
    params["iterations"] = int(args.iterations)
params["quiet"] = args.quiet
params["debug"] = args.debug
params["year"] = int(args.year) if args.year else None
params["week"] = int(args.week) if args.week else None
if args.config:
    params["config"] = args.config
if params["config"] and not os.path.isfile(params["config"]):
    logger.error("Could not access %s", params["config"])
    sys.exit(1)
if params["debug"]:
    print("Enabling debug")
    console.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

sanitize(params)

logger.debug("parameters:")
for params_key in params:
    logger.debug("\t%s: %s", params_key, params[params_key])

for command in params["commands"]:
    if command not in commands:
        logger.error("Unsupported command: %s", command)
        argParser.print_help()
        sys.exit(1)
    logger.info("calling %s", command)
    commands[command](params)
