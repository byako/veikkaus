"""
Main starting point
"""

import datetime
import getopt
import logging
import sys

from handies import load_and_print_draw
from fetch_results import get_draw
from gen_plot_source import gen_plot_source
from regenerate import refetch_all, regenerate_latest


logger = logging.getLogger("veikkilogger")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

params = {
    "year": None,
    "week": None,
    "command": None,
    "latest_file": "latest_ejackpot.json",
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
    "parse": load_and_print_draw,
    "regen": regenerate_latest,
    "refetch": refetch_all,
    "genplotsource": gen_plot_source,
    "help": _print_usage_and_exit,
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
    sys.argv[1:], "hw:y:", ["week", "year", "help"]
)

for opt, val in optlist:
    logger.debug("processing options: %s", opt)
    if opt in ["-h", "--help", "help"]:
        _print_usage_and_exit()
    elif opt in ["-y", "--year"]:
        params["year"] = int(val)
    elif opt in ["-w", "--week"]:
        params["week"] = int(val)
    else:
        logger.error("Unsupported parameter: %s", opt)
        _print_usage_and_exit()

if not leftovers:
    logger.error("command is missing")
    _print_usage_and_exit()

params["commands"] = leftovers

sanitize(params)

for command in leftovers:
    logger.debug("processing command %s", command)
    if command not in commands:
        logger.error("Unsupported command: %s", command)
        _print_usage_and_exit()
    logger.debug("calling %s", command)
    commands[command](params)
