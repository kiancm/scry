from enum import Enum
import argparse

import requests


class Actions(Enum):
    EV = "ev"
    SEARCH = "search"

class SearchOptions(Enum):
    PRICE = "price"
    INFO = "info"


def ev(args):
    sets = requests.get("https://api.scryfall.com/sets/").json()
    for s in sets["data"]:
        if args.code.upper() == s["code"].upper():
            return f"${_ev_url(s['search_uri']):.2f}"


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


def search(args):
    fuzzy = args.query.lower().replace(" ", "+")
    if SearchOptions(args.type) is Actions.PRICE:
        json = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={fuzzy}").json()
        return f"{json['name']}: ${json['usd']}"
    if SearchOptions(args.type) is Actions.INFO:
        text = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={fuzzy}&format=text").text
        return text


if __name__ == "main":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_search = subparsers.add_parser("search")
    parser_search.add_argument("type", type=str, default=SearchOptions.PRICE.value, choices=[e.value for e in SearchOptions])
    parser_search.add_argument("query", type=str)
    parser_search.set_defaults(func=search)

    parser_ev = subparsers.add_parser("ev")
    parser_ev.add_argument("code", type=str)
    parser_ev.set_defaults(func=ev)

    args = parser.parse_args()

    print(args.func(args))
