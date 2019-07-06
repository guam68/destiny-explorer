import argparse
import requests
from PIL import Image
import json
import textwrap
import copy
from colorama import init, Fore, Style
import credentials as cred
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


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

    display_options(card, args)


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


def find_pairings(card, args):
    txt_colors = {
        'red': Fore.RED,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'gray': Fore.WHITE
    }

    reset = Style.RESET_ALL

    sql2 = filter_results(True, args)
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
        if len(c_points) == 1:
            continue
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
            print(txt_colors[pair[1]['faction_code']] + space_adj(pair[0]) + reset + ' ' + 
                str(pair[1]['code']) + ' | ', end=' ')
        print()
    
    display_options(card, args)


def filter_results(is_pairing, args):
    card_types = {
        'char': 'character',
        'upgr': 'upgrade',
        'event': 'event',
        'supp': 'support',
        'dgrd': 'downgrade',
        'plot': 'plot'
    }

    colors = {
        'r': 'red',
        'g': 'gray',
        'b': 'blue',
        'y': 'yellow'
    }

    affinities = {
        'h': 'hero',
        'v': 'villain',
        'n': 'neutral'
    }
    
    sql2 = ''

    if args['card_set'] == 'all':
        if args['t_format'] == 'std':
            sql2 = '''
                where set_code in ('SoH', 'AoN', 'CONV', 'AtG', 'WotF', 'LEG', 'TPG', 'RIV') 
            '''
        elif args['t_format'] == 'tri':
            sql2 = '''
                where set_code in ('SoH', 'AoN', 'CONV') 
            '''
        else:
            sql2 = 'where deck_limit > 0' 
    else:
        sql2 = 'where set_code = \'' + args["card_set"] + '\''

    if is_pairing:
        return sql2

    if args['card_type'] != 'all':
        sql2 += ' and type_code = \'' + card_types[args['card_type']] + '\''

    card_colors = []
    for color in colors.keys():
        if color in args['color']:
            card_colors.append(colors[color])
    card_colors = 'in ' + str(tuple(card_colors)) if len(card_colors) > 1 else '= \'' + card_colors[0] + '\''
    sql2 += ' and faction_code ' + card_colors

    affin = []
    for aff in affinities.keys():
        if aff in args['affinity']:
            affin.append(affinities[aff])
    card_aff = 'in ' + str(tuple(affin)) if len(affin) > 1 else '= \'' + affin[0] + '\''
    sql2 += ' and affiliation_code ' + card_aff

    return sql2


def search(args):
    url = 'https://swdestinydb.com/api/public/card/' 
    card_id = input('\nEnter the card id or press enter to see card list ([a] for adv search, ' +
        '[q] to quit, [f] to change filters): ')
    if card_id == 'q':
        raise SystemExit
    elif card_id == 'f':
        change_filters(args)
    elif card_id == 'a':
        adv_search(args)
    else:
        response = requests.get(url + card_id)
        if response.status_code == 500:
            print('\nFilter choices: ' + str(args) + '\n')
            sql2 = filter_results(False, args)

            con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
            con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with con:
                cur = con.cursor()
                sql = 'select * from card ' + sql2
                cur.execute(sql)
                results = cur.fetchall()
                for result in results:
                    display_info(result[-1], args, False)
                print()
                search(args)
                
        else:
            card = response.json()
            display_info(card, args, True)
            display_options(card, args)


def adv_search(args):
    choice = input('\n[t] to search by card text or [enter] to search by card name: ')
    in_text = 'Enter text keyword: ' if choice == 't' else 'Enter character name: '
    sql1 = ' and card_text' if choice == 't' else ' and card_name'
    sql2 = filter_results(False, args)
    keyword = '%' + input(in_text) + '%'

    con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with con:
        cur = con.cursor()
        sql = ("select * from card " + sql2 + sql1 + " ilike '" + keyword + "'")
        cur.execute(sql)
        cards = cur.fetchall()
    
    for card in cards:
        display_info(card[-1], args, False)

    search(args)


def display_info(card, args, single):
    txt_colors = {
        'red': Fore.RED,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'gray': Fore.WHITE
    }
    reset = Style.RESET_ALL

    if single:
        print(txt_colors[card['faction_code']] + '\n' + card['name'])
        print('\tColor: ' + reset + card['faction_code'])
        print(txt_colors[card['faction_code']] + '\tAffinity: ' + reset + card['affiliation_name'])
        print(txt_colors[card['faction_code']] + '\tRarity: ' + reset + card['rarity_name'])
        try:
            print(txt_colors[card['faction_code']] + '\tSides: ' + reset + str(card['sides']))
        except KeyError:
            pass
        print(txt_colors[card['faction_code']] + '\tSet: ' + reset + card['set_name'])
        if card['cost']: print(txt_colors[card['faction_code']] + '\tCost: ' + reset + str(card['cost']))
        if card['health']: print(txt_colors[card['faction_code']] + '\tHealth: ' + reset + str(card['health']))
        if card['points']: print(txt_colors[card['faction_code']] + '\tPoints: ' + reset + str(card['points']))
        print(txt_colors[card['faction_code']] + '\tUnique: ' + reset + str(card['is_unique']))
        if card['text']: 
            wrapped = textwrap.wrap(txt_colors[card['faction_code']] + 'Text: \t' + reset + card['text'])
            for i, wrap in enumerate(wrapped):
                if i != 0:
                    wrap = '\t' + wrap
                print('\t' + wrap)
    else:
        print(txt_colors[card['faction_code']] + card['code'] + reset + '\t' + card['set_code'] + '\t' + 
            card['type_code'] + '    \t' + txt_colors[card['faction_code']] + space_adj(card['name']) + reset, end='')
        try:
            print('\tSides: ' + str(card['sides']))
        except KeyError:
            print()


def change_filters(args):
    flag = False
    filters = {
        't': 'card_type',
        'a': 'affinity',
        'c': 'color',
        'f': 'format',
        's': 'card_set'
    }
    filter_options = {
        't': ('Options: all, char, supp, upgr, event, plot, dgrd', 
            ['all', 'char', 'supp', 'upgr', 'event', 'plot', 'dgrd']),
        'a': ('Options: [h]ero, [v]illain, [n]eutral', 'hvn'),
        'c': ('Options: [g]ray, [y]ellow, [b]lue, [r]ed', 'gybr'),
        'f': ('Options: inf, std, tri', ['inf', 'std', 'tri']),
        's': ('Options: AW, SoR, EaW, TPS, LEG, RIV, WotF, AtG, CONV, AoN, SoH', 
            ['AW', 'SoR', 'Eaw', 'TPS', 'LEG', 'RIV', 'WotF', 'AtG', 'CONV', 'AoN', 'SoH'])
    }

    while not flag:
        print('Select a filter to change.')
        _filter = input('[t]ype, [a]ffinity, [c]olor, [f]ormat, [s]et: ')
        if _filter in filters:
            print('\nSelect a filter')
            option = input(filter_options[_filter][0] + ': ')
            if _filter == 'a' or _filter == 'c':
                for char in option:
                    if char in filter_options[_filter][1]:
                        continue 
                    else:
                        print('Not a valid filter option.')
                        break
                args[filters[_filter]] = option 
            elif option in filter_options[_filter][1]:
                args[filters[_filter]] = option 
        cont = input('Enter [r] to return to search or any key to change another filter: ')
        flag = True if cont == 'r' else False
    
    search(args)


def display_options(card, args):
    if card['type_code'] == 'character':
        option = input('\nEnter [i] to show card img, [p] for character pairings, ' +
            '[f] to change filters, or [s] to search another card:\n')
    else:
        option = input('\nEnter [i] to show card img or [s] to search another card:\n')
    
    if option not in 'ispf':
        print('Not a valid option.')

    if option == 'i':
        show_card(card['set_code'], card['position'], card, args)
    elif option == 's':
        search(args)
    elif option == 'p' and card['type_code'] == 'character':
        find_pairings(card, args) 
    elif option == 'f':
        change_filters(args)


def space_adj(string):
    if len(string) < 20:
        while len(string) < 20:
            string = string + ' '
    return string[0:19]


def main():
    init()
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-t', dest='card_type', default='all', help='Limit card pool by card type ' +
        'Options: [all, char, supp, upgr, event, plot, dgrd]\n') 
    parser.add_argument('-a', dest='affinity', default='hvn', help='Limit card pool by affinity. ' +
        'Options: [h]ero, [v]illain, [n]eutral\n' +
        '\tNote: May contain any combination of the options\n' +
        '\tex. -a vn\n \n')
    parser.add_argument('-c', dest='color', default='rgby', help='Limit card pool by color. ' +
        'Options: [g]ray, [y]ellow, [b]lue, [r]ed\n' +
        '\tNote: May contain any combination of the options\n' +
        '\tex. -c rbg\n \n')
    parser.add_argument('-f', dest='t_format', default='std', help='Restrict card pool by format. Options: [inf, std, tri]')
    parser.add_argument('-s', dest='card_set', default='all', help='Restrict card pool by set. ' +
        'Options: [AW, SoR, EaW, TPS, LEG, RIV, WotF, AtG, CONV, AoN, SoH]\n \n')

    args = parser.parse_args()

    search(vars(args))


if __name__ == "__main__":
    main() 