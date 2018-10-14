import argparse
import requests

def ev(code):
    sets = requests.get('https://api.scryfall.com/sets/').json()
    for s in sets['data']:
        if code.upper() == s['code'].upper():
            return '${:.2f}'.format(_ev_url(s['search_uri']))

def _ev_url(url):
    multipliers = {'mythic': .3, 'rare': .59, 'uncommon': 1.35, 'common': 0}
    total = 0
    set_list = requests.get(url).json()
    cards = set_list['data']
    for card in cards:
        if 'usd' in card:
            total += multipliers[card['rarity']] * float(card['usd'])
    if set_list['has_more']:
        return total + _ev_url(set_list['next_page'])
    else:
        return total

def search(query, search_type='price'):
    fuzzy = query.lower().replace(' ', '+')
    if search_type == 'price':
        json = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + fuzzy).json()
        return json['name'] + ': $' + json['usd']
    if search_type == 'info':
        text = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + fuzzy + "&format=text").text
        return text
    # if json['object'] != 'error':
    #     return f[form]
    # return ValueError(json['details'])

if __name__ == 'main':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', default='ev', choices=['ev', 'price', 'info'])
    parser.add_argument('target', type=str)
    args = parser.parse_args()
    try:
        if args.action == 'ev':
            print(ev(args.target))
        else:
            print(search(args.target, search_type=args.action))
    except Exception as e:
        raise e


# def func_list(args):
#     func_args = {'ev': ev, 
#                  'price': price,
#                  'info'  : info}
#     arg1 = args[0]
#     print()
#     for arg in args[1:]:
#         if arg1 == 'ev':
#             print(arg.upper() + ': ', end = '')
#         try:
#             if arg1 == 'ev':
#                 print(func_args[arg1](arg))
#             else:
#                 print(func_args[arg1](arg) + '\n')
#         except ValueError as e:
#             print(str(e) + '\n')

# func_list(sys.argv[1:])