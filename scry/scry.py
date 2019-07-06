import sys
import argparse
from enum import Enum

import requests

from .utils import Factory


search_factory = Factory()


def ev(args):
    sets = requests.get("https://api.scryfall.com/sets/").json()
    for s in sets["data"]:
        code = s["code"]
        url = s["url"]
        if args.code.upper() == code.upper():
            return f"${_ev_url(url):.2f}"


def _ev_url(url):
    multipliers = {"mythic": 0.3, "rare": 0.59, "uncommon": 1.35, "common": 0}
    set_list = requests.get(url).json()
    cards = set_list["data"]
    total = sum(
        multipliers[card["rarity"]] * float(card["prices"]["usd"])
        for card in cards
        if safe(card)
    )

    if set_list["has_more"]:
        return total + _ev_url(set_list["next_page"])

    return total


def safe(card):
    return (
        card
        and "prices" in card
        and card["prices"]
        and "usd" in card["prices"]
        and card["prices"]["usd"]
    )


def search(args):
    return search_factory[args.type](args.query)


@search_factory
def price(query):
    fuzzy = query.lower().replace(" ", "+")
    json = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={fuzzy}").json()
    return f"{json['name']}: ${json['prices']['usd']}"

def card_border(line, length):
    return f"|{line}{(length - len(line)) *  ' '}|\n"

@search_factory
def info(query):
    fuzzy = query.lower().replace(" ", "+")
    text = requests.get(
        f"https://api.scryfall.com/cards/named?fuzzy={fuzzy}&format=text"
    ).text
    lines = text.strip().splitlines()
    border_len = max(len(line) for line in lines)
    outline =  f"|{'-' * border_len}|\n"
    output_lines = [card_border(line, border_len) for line in lines] 
    rules = "".join(output_lines[2:])
    output = outline.join([*output_lines[:2], rules])

    return f"+{'-' * border_len}+\n{output}+{'-' * border_len}+"


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_search = subparsers.add_parser("search")
    parser_search.add_argument(
        "type", type=str, choices=search_factory._builders.keys()
    )
    parser_search.add_argument("query", type=str)
    parser_search.set_defaults(func=search)

    parser_ev = subparsers.add_parser("ev")
    parser_ev.add_argument("code", type=str)
    parser_ev.set_defaults(func=ev)

    args = parser.parse_args()

    if len(sys.argv) > 1:
        print(args.func(args))
    else:
        parser.print_help()