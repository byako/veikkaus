#!/usr/bin/python3
"""
Fetch single result from Veikkaus API, parse and save it
"""

from __future__ import print_function

import datetime
import getopt
import json
import os.path
import sys
import time

import requests

# the veikkaus site address
VEIKKAUS_HOST = "https://www.veikkaus.fi"

# required headers
VEIKKAUS_HEADERS = {
    "Content-type": "application/json",
    "Accept": "application/json",
    "X-ESA-APi-Key": "ROBOT",
}


def _print_usage():
    print(
        """\n Usage:
-h prints this help
-w <week number[1..53]>
-y <year number[2010..$CurYear]>"""
    )
    sys.exit(0)


def append_to_latest(text, params):
    """Append to the end of $LATEST_FILE text string"""
    latest_file = "latest_%s.json" % params["game"]
    if os.path.exists(latest_file):
        try:
            print("appending to %s : %s" % (latest_file, text))
            out_file = open(latest_file, "a")
            out_file.write(text + ",\n")
            out_file.flush()
            out_file.close()
        except IOError as woat:
            print("Failed to append. Error: " + woat)
    else:
        print("could not find latest file: " + latest_file)


def save_to_file(filename, text):
    """Save argument text to argument filename file if it does not exist"""
    print("saving to file " + filename)
    if os.path.exists(filename):
        print("file already exists: " + filename)
        return False

    try:
        out_file = open(filename, "w")
        out_file.write(text)
        out_file.flush()
        out_file.close()
    except IOError as woat:
        print("Failed saving to file: %s, error: %s" % (filename, woat))
        return False
    return True


def parse_arguments(arguments):
    """Get week number and year out of arguments"""
    optlist, _ = getopt.getopt(arguments, "ha:w:y:g:")
    params = {
        "username": "",
        "passowrd": "",
        "year": "1970",
        "week": "54",
        "game": "ejackpot",
    }
    for opt, val in optlist:
        if opt == "-h":
            _print_usage()
        elif opt == "-y":
            params["year"] = int(val)
        elif opt == "-w":
            params["week"] = int(val)
    return params


def get_draw(params):
    """Fetch draw result from VEIKKAUS_HOST"""
    rurl = "%s/api/draw-results/v1/games/%s/draws/by-week/%d-W%02d" % (
        VEIKKAUS_HOST,
        params["game"],
        params["year"],
        params["week"],
    )
    req = requests.get(rurl, verify=True, headers=VEIKKAUS_HEADERS)
    if req.status_code == 200:
        try:
            draw = req.json()[0]
            latest_result = {
                "year": 1970,
                "week": 1,
                "numbers": [],
                "adds": [],
                "date": "01.01",
            }
            draw_time = time.localtime(draw["drawTime"] / 1000)
            latest_result["year"] = str(params["year"])
            latest_result["week"] = str(params["week"])
            latest_result["date"] = time.strftime("%m.%d", draw_time)
            for prim in draw["results"][0]["primary"]:
                latest_result["numbers"].append(int(prim))
            for addit in draw["results"][0]["secondary"]:
                latest_result["adds"].append(int(addit))
            prize = draw["jackpots"][0]["amount"]
            print(
                "draw: %s (%s / %s.%s), prize %s"
                % (
                    draw["id"],
                    latest_result["week"],
                    latest_result["year"],
                    latest_result["date"],
                    prize
                )
            )
            print(
                "  %s / %s"
                % (
                    json.dumps(latest_result["numbers"]),
                    json.dumps(latest_result["adds"]),
                )
            )
            for prize in draw["prizeTiers"]:
                print(
                    "%6d : %8d.%02d : %10s"
                    % (
                        prize["shareCount"],
                        prize["shareAmount"] / 100,
                        prize["shareAmount"] % 100,
                        prize["name"],
                    ),
                )
            print("")
            s_file = "results/%s_%s_%s.json" % (
                params["game"],
                params["year"],
                params["week"],
            )
            if save_to_file(s_file, req.text,):
                append_to_latest(
                    json.dumps(latest_result, separators=(",", ":")), params
                )
        except Exception as woat:  # pylint: disable=broad-except
            print("Request failed:" + woat)
    else:
        print("request failed: " + req.text)


def starter(arguments):
    """Validate arguments and process results"""
    params = parse_arguments(arguments)
    if params["week"] == "54" or params["year"] == "1970":
        _print_usage()
    elif int(params["year"]) < 2009:
        print("oldest results are from 2009")
    elif int(params["year"]) > datetime.datetime.now().year:
        print("You want results from future? I don't think so.")
    elif int(params["week"]) < 0 or int(params["week"]) > 53:
        print("Wrong week number")
    else:
        get_draw(params)
        sys.exit(0)
    _print_usage()


if __name__ == "__main__":
    starter(sys.argv[1:])
