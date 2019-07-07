import sys
import argparse
from enum import Enum

import requests

from .utils import Factory


search_factory = Factory()


def ev(args):
    sets = requests.get("https://api.scryfall.com/sets/").json()
    results = [
        f"{s['name']} ({s['code'].upper()}): ${_ev_url(s['search_uri']):.2f}"
        for acode in args.codes
        for s in sets["data"]
        if acode.upper() == s["code"].upper()
    ]

    return "\n".join(results)


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
    split_lines = [[split + "." for split in line.split(".") if split] if len(line) > 150 else [line] for line in lines]
    flat_lines = [fline.strip() for sline in split_lines for fline in sline if fline]
    border_len = max(len(line) for line in flat_lines)
    outline = f"|{'-' * border_len}|\n"
    output_lines = [card_border(line, border_len) for line in flat_lines]
    rules = "".join(output_lines[2:])
    output = outline.join([*output_lines[:2], rules])

    import pdb; pdb.set_trace()

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
    parser_ev.add_argument("codes", type=str, nargs="+")
    parser_ev.set_defaults(func=ev)

    args = parser.parse_args()

    print(args.func(args))
