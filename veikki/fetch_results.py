"""
Fetch single result from Veikkaus API, parse and save it
"""
import json
import logging
import os.path

import requests

from handies import parse_draws


logger = logging.getLogger("veikkilogger")

# the veikkaus site address
VEIKKAUS_HOST = "https://www.veikkaus.fi"

# required headers
VEIKKAUS_HEADERS = {
    "Content-type": "application/json",
    "Accept": "application/json",
    "X-ESA-APi-Key": "ROBOT",
}


def append_to_latest(new_results: list, params: dict) -> None:
    """Append new record to the end of latest file"""
    logger.info("appending new result to %s", params["latest_file"])
    if os.path.exists(params["latest_file"]):
        with open(params["latest_file"], "r+") as json_file:
            results = json.load(json_file)
            for new_result in new_results:
                if results[-1]["id"] != new_result["id"]:
                    results.append(new_result)
                else:
                    logger.info("skipping previously saved result %d", new_result["id"])
            json_file.seek(0)
            json.dump(results, json_file)
    else:
        logger.error("could not find latest file: %s", params["latest_file"])


def save_result_to_file(filename: str, text: str) -> bool:
    """Save argument text to argument filename file if it does not exist"""
    logger.info("Saving to file %s", filename)
    if os.path.exists(filename):
        logger.warn("file %s already exists, overwriting", filename)

    try:
        out_file = open(filename, "w")
        out_file.write(text)
        out_file.flush()
        out_file.close()
    except IOError as woat:
        logger.error("Failed saving to file: %s, error: %s", filename, woat)
        return False

    return True


def get_week_results(params: dict) -> list:
    """Fetch draw result from VEIKKAUS_HOST"""
    rurl = "%s/api/draw-results/v1/games/ejackpot/draws/by-week/%d-W%02d" % (
        VEIKKAUS_HOST,
        params["year"],
        params["week"],
    )
    req = requests.get(rurl, verify=True, headers=VEIKKAUS_HEADERS)
    latest_results = []
    if req.status_code == 200:
        try:
            json_full_result = req.json()
            latest_results = parse_draws(json_full_result)
            s_file = "results/ejackpot_%s_%s.json" % (
                params["year"],
                params["week"],
            )
            if save_result_to_file(s_file, req.text):
                append_to_latest(latest_results, params)
        except Exception as woat:  # pylint: disable=broad-except
            logger.error("Request failed: %s", woat)
    else:
        logger.error("request failed: %s", req.text)

    return latest_results
