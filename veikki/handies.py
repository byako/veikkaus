"""
common functions for modules
"""
from copy import deepcopy
import json
import os
import time
import logging

logger = logging.getLogger("veikkilogger")

TEMPLATE_DRAW = {
    "id": None,
    "week": None,
    "year": None,
    "date": None,
    "primary": [],
    "adds": [],
    "scores": [],
    "jackpot_value": None,
    "jackpot_won": False,
    "flags": {"jp": False},
}


def print_latest_result_date(params: dict) -> str:
    """
    get the date of latest saved result
    """
    if os.path.exists(params["latest_file"]):
        with open(params["latest_file"], "r+") as json_file:
            results = json.load(json_file)
            logger.error(
                "%s / %s : %s",
                results[-1]["year"],
                results[-1]["week"],
                results[-1]["date"],
            )
    else:
        logger.error("could not find latest file: %s", params["latest_file"])


def print_draw(parsed_draw: dict) -> None:
    """
    parsed_draw is json from veikkaus results
    """
    logger.info(
        "draw: %s %s / %s (%s), prize %s",
        parsed_draw["id"],
        parsed_draw["year"],
        parsed_draw["week"],
        parsed_draw["date"],
        parsed_draw["jackpot_value"],
    )
    logger.info(
        "  %s / %s",
        json.dumps(parsed_draw["primary"]),
        json.dumps(parsed_draw["adds"]),
    )
    for prize in parsed_draw["scores"]:
        logger.info(
            "%6d : %8d.%02d : %10s",
            prize["shareCount"],
            prize["shareAmount"] / 100,
            prize["shareAmount"] % 100,
            prize["name"],
        )


def parse_draw(json_full_draw) -> dict:
    """
    Structure of draw record has changed over time, this is a safe parser that
    takes only needed data from full draw info
    """
    draw = deepcopy(TEMPLATE_DRAW)
    full_draw = None

    if isinstance(json_full_draw, dict):
        full_draw = json_full_draw["draws"][0]
    elif isinstance(json_full_draw, list):
        full_draw = json_full_draw[0]
    else:
        err_msg = "Could not parse draw: %s" % str(json_full_draw)
        logger.error(err_msg)
        raise ValueError(err_msg)

    draw_time = time.localtime(full_draw["drawTime"] / 1000)
    draw["id"] = full_draw["id"]
    draw["year"] = time.strftime("%Y", draw_time)
    draw["week"] = str(int(time.strftime("%W", draw_time)) + 1)
    draw["date"] = time.strftime("%d.%m", draw_time)
    draw["primary"] = [int(x) for x in full_draw["results"][0]["primary"]]
    draw["adds"] = [int(x) for x in full_draw["results"][0]["secondary"]]
    draw["jackpot_value"] = (
        full_draw["jackpots"][0]["amount"] if "jackpots" in full_draw else -1
    )
    draw["scores"] = full_draw["prizeTiers"]
    top_tier = [
        tier for tier in full_draw["prizeTiers"] if tier["name"] == "5+2 oikein"
    ][0]
    draw["jackpot_won"] = True if top_tier["shareCount"] > 0 else False
    return draw


def load_draw_from_file(params: dict) -> dict:
    """
    Load from file previously fetched draw result
    Returns parsed draw result
    """
    logger.debug("Loading results for %s / %s", params["year"], params["week"])

    filename = f'results/ejackpot_{params["year"]}_{params["week"]}.json'
    with open(filename, "r") as json_file:
        return parse_draw(json.load(json_file))


def load_and_print_draw(params: dict) -> None:
    """
    Load from file previously fetched draw result and print it
    """
    draw_result = load_draw_from_file(params)
    print_draw(draw_result)
