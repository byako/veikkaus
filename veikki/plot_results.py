"""
Generate stat graphs and save to files
"""
import json
from multiprocessing import Pool
import os
import logging
from matplotlib import pyplot
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

logger = logging.getLogger("veikkilogger")
logger.setLevel(logging.DEBUG)

CONFIG = {"numbersLimit": 50, "additionalLimit": 10}


def plot_one(p_tuple):
    """ test plotting into file """
    (primary, average, filename) = p_tuple
    if os.path.isfile(filename):
        logger.debug("skipping %s: file exists", filename)
        return
    logger.debug("plotting %s", filename)
    avg_list = [average] * CONFIG["numbersLimit"]
    nums = [idx for idx in range(1, CONFIG["numbersLimit"] + 1)]

    fig, axes = pyplot.subplots()
    fig.set_size_inches(13, 2.5)
    axes.yaxis.set_major_locator(MultipleLocator(5))
    axes.yaxis.set_minor_locator(AutoMinorLocator(5))
    axes.xaxis.set_major_locator(MultipleLocator(5))
    axes.xaxis.set_minor_locator(AutoMinorLocator(5))
    axes.plot(nums, primary, label="primary")
    axes.plot(nums, avg_list, label="average")
    axes.legend()
    axes.grid(which="both")
    axes.grid(which="minor", alpha=0.2)
    axes.grid(which="major", alpha=0.5)
    axes.set_xlim(1, CONFIG["numbersLimit"])
    # axes.set_facecolor("xkcd:grey")
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

    to_plot = []
    for draw in results:
        for prim in draw["primary"]:
            common_stats[prim - 1] += 1
            primary_stats[prim - 1] += 1
        for sec in draw["adds"]:
            common_stats[sec - 1] += 1
            additional_stats[sec - 1] += 1

        filename = f'png/ejackpot_{draw["year"]}_{draw["week"]}.png'
        average_stats = sum(primary_stats) / CONFIG["numbersLimit"]
        to_plot.append((primary_stats, average_stats, filename))
    with Pool(2) as p:
        p.map(plot_one, to_plot)
