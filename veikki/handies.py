"""
common functions for modules
"""
from copy import deepcopy
import json
import datetime
import os
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


def load_latest_file(params: dict) -> list:
    """
    return JSON-parsed contents of latest results file
    """
    if os.path.exists(params["latest_file"]):
        with open(params["latest_file"], "r+") as json_file:
            results = json.load(json_file)
            return results
    else:
        logger.error("could not find latest file: %s", params["latest_file"])
    return []


def print_latest_result_date(params: dict) -> str:
    """
    get the date of latest saved result
    """
    results = load_latest_file(params)
    logger.debug(
        "%s / %s : %s",
        results[-1]["year"],
        results[-1]["week"],
        results[-1]["date"],
    )


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
        f'{parsed_draw["jackpot_value"]/100:,}',
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


def parse_draws(json_full_result) -> list:
    """
    Structure of draw record has changed over time, this is a safe parser that
    takes only needed data from full draw info
    """
    draw = deepcopy(TEMPLATE_DRAW)

    full_draws = None
    if isinstance(json_full_result, dict):
        full_draws = json_full_result["draws"]
    elif isinstance(json_full_result, list):
        full_draws = json_full_result
    else:
        err_msg = "Could not parse draw: %s" % str(json_full_result)
        logger.error(err_msg)
        raise ValueError(err_msg)

    draws = []
    for _, full_draw in enumerate(full_draws):
        draw_date = datetime.datetime.fromtimestamp(
            full_draw["drawTime"] / 1000
        )
        draw["id"] = full_draw["id"]
        draw["year"] = draw_date.isocalendar()[0]
        draw["week"] = draw_date.isocalendar()[1]
        draw["date"] = f"{draw_date.year}.{draw_date.month}.{draw_date.day}"
        draw["primary"] = [int(x) for x in full_draw["results"][0]["primary"]]
        draw["adds"] = [int(x) for x in full_draw["results"][0]["secondary"]]
        draw["jackpot_value"] = (
            full_draw["jackpots"][0]["amount"]
            if "jackpots" in full_draw
            else -1
        )
        draw["scores"] = full_draw["prizeTiers"]
        top_tier = [
            tier
            for tier in full_draw["prizeTiers"]
            if tier["name"] == "5+2 oikein"
        ][0]
        if top_tier["shareCount"] > 0:
            draw["jackpot_won"] = True
        draws.append(deepcopy(draw))

    return draws


def load_draws_from_file(params: dict) -> list:
    """
    Load from file previously fetched draw result
    Returns parsed draw result
    """
    filename = f'results/ejackpot_{params["year"]}_{params["week"]}.json'
    if not params["quiet"]:
        logger.debug("Loading result file %s", filename)
    if os.path.isfile(filename):
        with open(filename, "r") as json_file:
            return parse_draws(json.load(json_file))
    else:
        logger.error("Cannot find file %s", filename)
    return None


def load_and_print_draw(params: dict) -> None:
    """
    Load from file previously fetched draw result and print it
    """
    draw_result = load_draws_from_file(params)
    print_draw(draw_result)
