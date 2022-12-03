"""
post-processing results/*json files into:
- latest.json
- plot sources
"""
from datetime import datetime
import json
import logging
import os
import subprocess

from fetch_results import get_week_results
from handies import parse_draws


logger = logging.getLogger("veikkilogger")
logger.setLevel(logging.DEBUG)


def regenerate_latest(params) -> None:
    """
    Read through results/ folder and generate new latest.json file
    """
    # this is unix-only, but with current file name format is the only option
    files = subprocess.check_output(
        "ls -1v results/", stderr=subprocess.STDOUT, shell=True
    ).decode()
    logger.debug("re-generating latest_ejackpot.json")
    files = files.split("\n")
    logger.info("got %d files", len(files))
    results = []
    for filename in files:
        if not filename:
            continue
        filepath = os.path.join("results", filename)
        logger.debug("%s", filepath)
        with open(filepath) as draw_file:
            draws = parse_draws(json.load(draw_file))
            if (
                f'ejackpot_{draws[0]["year"]}_{draws[0]["week"]}.json'
                != filename
            ):
                logger.error(
                    "filename doesn't match content %s: %s / %s",
                    filename,
                    draws[0]["year"],
                    draws[0]["week"],
                )
            for result in draws:
                results.append(result)

    with open(params["latest_file"], "w") as latest_file:
        logger.debug("Saving new %s", params["latest_file"])
        json.dump(results, latest_file)

    return 0


def refetch_all(params: dict) -> None:
    """
    Delete existing result files and re-fetche them all again
    """
    now = datetime.now()
    w52 = {}
    for idx_year in range(2012, (now.year + 1)):
        params["year"] = idx_year
        week_range_start = 1
        week_range_limit = 54

        if params["year"] == now.year:
            # do not fetch current week
            week_range_limit = now.isocalendar()[1]

        if params["year"] == 2012:
            week_range_start = 12

        for idx_week in range(week_range_start, week_range_limit):
            params["week"] = idx_week
            logger.debug("fetching %s / %s", params["year"], params["week"])
            w53 = get_week_results(params)
            if idx_week == 52:
                w52 = w53
            elif idx_week == 53:
                if w52[0]["id"] == w53[0]["id"]:
                    filename = (
                        f'ejackpot_{params["year"]}_{params["week"]}.json'
                    )
                    filepath = os.path.join("results", filename)
                    logger.debug("No w53 result, deleting file %s", filepath)
                    os.remove(filepath)
    regenerate_latest(params)  # in case some results got deleted
