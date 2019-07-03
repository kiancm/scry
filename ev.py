from enum import Enum
import argparse

import requests


class Actions(Enum):
    EV = "ev"
    PRICE = "price"
    INFO = "info"


def ev(code):
    sets = requests.get("https://api.scryfall.com/sets/").json()
    for s in sets["data"]:
        if code.upper() == s["code"].upper():
            return "${:.2f}".format(_ev_url(s["search_uri"]))


def _ev_url(url):
    multipliers = {"mythic": 0.3, "rare": 0.59, "uncommon": 1.35, "common": 0}
    set_list = requests.get(url).json()
    cards = set_list["data"]
    total = sum(
        multipliers[card["rarity"]] * float(card["usd"])
        for card in cards
        if "usd" in card
    )

    if set_list["has_more"]:
        return total + _ev_url(set_list["next_page"])
    else:
        return total


def search(query, search_type=Actions.PRICE):
    fuzzy = query.lower().replace(" ", "+")
    if search_type is Actions.PRICE:
        json = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={fuzzy}").json()
        return f"{json["name"]}: ${json["usd"]}
    if search_type is Actions.INFO:
        text = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={fuzzy}&format=text").text
        return text


if __name__ == "main":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action", default=Actions.EV.value, choices=[e.value for e in Actions]
    )
    parser.add_argument("target", type=str)
    args = parser.parse_args()
    if Actions(args.action) is Actions.EV:
        print(ev(args.target))
    else:
        print(search(args.target, search_type=Actions(args.action)))
