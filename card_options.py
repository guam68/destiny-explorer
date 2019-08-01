import copy

from colorama import Fore, Style
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import credentials as cred
import requests
from PIL import Image


def get_proxy_dice(base_card):
    proxies = []
    off_proxies = []
    con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with con:
        cur = con.cursor()
        sql = ("select * from card where has_die = 'True'" )
        cur.execute(sql)
        cards = cur.fetchall()

    for card in cards:
        card_dict = dict(card[-1])
        proxy_sides = list(card_dict['sides'])
        if proxy_sides == base_card['sides']:
            if base_card['name'] != card_dict['name']:
                proxies.append([card_dict['name'], card_dict['code']])
        else:
            matched_sides = 0
            for i, side in enumerate(base_card['sides']):
                for j, p_side in enumerate(proxy_sides):
                    if p_side == side:
                        matched_sides += 1
                        proxy_sides[j] = None
                        break
            if matched_sides == 5:
                off_proxies.append([card_dict['name'], card_dict['code'], card_dict['sides']])
    
    if proxies:
        for proxy in proxies:
            print(proxy)
    if off_proxies:
        for proxy in off_proxies:
            print(proxy)
    else:
        print('No proxy dice found')


def get_pair(chars, pairs):
    for i, pair in enumerate(pairs):
        if int(pair[-1]) > 26:
            continue
        else:
            pair_copy = copy.deepcopy(pair)
            tot_cost = pair_copy.pop(-1)
            
        for char in chars:
            char_obj = dict(char[-1])
            c_points = char_obj['points'].split('/')
            for j, c_cost in enumerate(c_points):
                matched_name = 'e' + char_obj['name'] if j > 0 else char_obj['name']
                cost = tot_cost + int(c_cost)
                if cost <= 30:
                    pairs.append(pair_copy + [[matched_name, char_obj], cost])

    return pairs


def find_pairings(explorer, card, args):
    txt_colors = {
        'red': Fore.RED,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'gray': Fore.WHITE
    }

    reset = Style.RESET_ALL

    sql2 = explorer.filter_results(True)
    types = str((card['affiliation_code'], 'neutral'))

    con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with con:
        cur = con.cursor()
        sql = ("select * from card " + sql2 + " and affiliation_code in " + types +
            " and type_code = 'character'")
        cur.execute(sql)
        chars = cur.fetchall()

    points = card['points'].split('/')
    if len(points) > 1:
        dice = input('Enter [e] for elite or [s] for single die: ')
        if dice not in 'es':
            dice = 'e'
            print('Not a valid option. Matching for elite.')
    else:
        dice = 's'
    p_cost = points[0] if dice == 's' else points[1]
    searched_name = 'e' + card['name'] if dice == 'e' else card['name']

    pairs = [] 
    for char in chars:
        char_obj = dict(char[-1])
        c_points = char_obj['points'].split('/')

        for i, c_cost in enumerate(c_points):
            matched_name = 'e' + char_obj['name'] if i > 0 else char_obj['name']
            tot_cost = int(p_cost) + int(c_cost)
            if tot_cost <= 30:
                pairs.append([[matched_name, char_obj], tot_cost])
    
    multi_pair = input('Enable multi-pair? (y/n): ')
    if multi_pair == 'y':
        pairs_list = get_pair(chars, pairs)
    else:
        pairs_list = pairs

    for paired in pairs_list:
        point_color = Fore.RESET
        pair_point = paired.pop(-1)
        if pair_point <= 26:
            point_color = Fore.MAGENTA
         

        print(point_color + str(pair_point) + reset + ' - ' + txt_colors[card['faction_code']] + searched_name + 
            reset + ' | ', end=' ')

        for pair in paired:
            print(txt_colors[pair[1]['faction_code']] + explorer.space_adj(pair[0]) + reset + ' ' + 
                str(pair[1]['code']) + ' | ', end=' ')
        print()
    
    explorer.display_options(card)


def show_card(set_code, card_num, card, args):
    codes = {
        'AW': ['SWD03', 'SWD02', 'SWD03_'],
        'SoR': 'SWD04_',
        'EaW': 'SWD07_',
        'TPG': 'SWD08_',
        'LEG': 'SWD11a_',
        'RIV': 'SWD06_',
        'WotF': 'SWD12a_',
        'AtG': 'SWD13a_',
        'CONV': 'SWD16a_',
        'AoN': 'SWD17_',
        'SoH': 'SWD18_'
    }

    code = codes[set_code] if set_code != 'AW' else codes[set_code][0]
    url = 'http://lcg-cdn.fantasyflightgames.com/swd/' + code + str(card_num) + '.jpg'
    response = requests.get(url)

    if response.status_code == 403 and set_code == 'AW':
        i = 1
        while response.status_code == 403:
            url = 'http://lcg-cdn.fantasyflightgames.com/swd/' + codes[set_code][i] + str(card_num) + '.jpg'
            response = requests.get(url)
            i = i + 1

    with open('card_img.jpg', 'wb') as f:
        f.write(response.content)

    img = Image.open('card_img.jpg')
    img.show()
