"""
Main starting point
"""

import datetime
import getopt
import logging
import os
import sys

from handies import load_and_print_draw, print_latest_result_date
from fetch_results import get_draw
from plot_results import plot_all
from process import process
from regenerate import refetch_all, regenerate_latest


logger = logging.getLogger("veikkilogger")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

params = {
    "year": None,
    "week": None,
    "commands": [],
    "latest_file": "latest_ejackpot.json",
    "config": "config.ini",
    "iterations": 0,
    "quiet": False,
}


def _print_usage_and_exit(_=None):
    print(
        """
Usage: %s [command]
    command: %s
"""
        % (sys.argv[0], ", ".join(commands.keys()))
    )
    sys.exit(1)


commands = {
    "fetch": get_draw,
    "help": _print_usage_and_exit,
    "latest": print_latest_result_date,
    "parse": load_and_print_draw,
    "plot": plot_all,
    "process": process,
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


if not sys.version.startswith("3.7"):
    logger.error("Python 3.7 or newer is required")
    sys.exit(0)

optlist, leftovers = getopt.getopt(
    sys.argv[1:], "hqw:y:i:", ["week", "year", "help"]
)

for opt, val in optlist:
    if opt in ["-h", "--help", "help"]:
        _print_usage_and_exit()
    elif opt in ["-i", "--iterations"]:
        params["iterations"] = int(val)
    elif opt in ["-q", "--quiet"]:
        params["quiet"] = True
    elif opt in ["-y", "--year"]:
        params["year"] = int(val)
    elif opt in ["-w", "--week"]:
        params["week"] = int(val)
    elif opt in ["-c", "--config"]:
        params["config"] = val
        if not os.path.isfile(val):
            logger.error("Could not access %s", val)
            sys.exit(1)
    else:
        logger.error("Unsupported parameter: %s", opt)
        _print_usage_and_exit()

if not leftovers:
    logger.error("command is missing")
    _print_usage_and_exit()

params["commands"] = leftovers

sanitize(params)

logger.debug("settings:")
for params_key in params:
    logger.debug("\t%s: %s", params_key, params[params_key])

for command in leftovers:
    if command not in commands:
        logger.error("Unsupported command: %s", command)
        _print_usage_and_exit()
    logger.debug("calling %s", command)
    commands[command](params)
