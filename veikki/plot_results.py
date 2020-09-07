"""
Generate stat graphs and save to files
"""
import json
import logging
import os.path
from matplotlib import pyplot
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

logger = logging.getLogger("veikkilogger")
logger.setLevel(logging.DEBUG)

CONFIG = {"numbersLimit": 50, "additionalLimit": 10}


def plot_one(primary: list, average: int, filename: str):
    """ test plotting into file """

    avg_list = [average] * CONFIG["numbersLimit"]
    nums = [idx for idx in range(1, CONFIG["numbersLimit"] + 1)]

    fig, ax = pyplot.subplots()
    fig.set_size_inches(13, 2.5)
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.plot(nums, primary, label="primary")
    ax.plot(nums, avg_list, label="average")
    ax.legend()
    ax.grid(which="both")
    ax.grid(which="minor", alpha=0.2)
    ax.grid(which="major", alpha=0.5)
    ax.set_xlim(1, CONFIG["numbersLimit"])
    fig.tight_layout()

    fig.savefig(filename, dpi=100)
    pyplot.close(fig)


def plot_all(params):
    """make sure all available results have corresponding plot"""
    common_stats = [0] * CONFIG["numbersLimit"]
    primary_stats = [0] * CONFIG["numbersLimit"]
    additional_stats = [0] * CONFIG["additionalLimit"]
    average_stats = 0

    results = None

    with open(params["latest_file"]) as latest_file:
        results = json.load(latest_file)
        logger.debug("results found: %d", len(results))

    for draw in results:
        for prim in draw["primary"]:
            common_stats[prim - 1] += 1
            primary_stats[prim - 1] += 1
        for sec in draw["adds"]:
            common_stats[sec - 1] += 1
            additional_stats[sec - 1] += 1

        filename = f'png/ejackpot_{draw["year"]}_{draw["week"]}.png'
        average_stats = sum(primary_stats) / CONFIG["numbersLimit"]
        if not os.path.isfile(filename):
            logger.debug("plotting %s %s", draw["year"], draw["week"])
            plot_one(primary_stats, average_stats, filename)
