import argparse
import requests
from PIL import Image
import json
import textwrap
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
        'AoN': 'SWD17_'
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


def find_pairings(card, args):
    sql2 = filter_results(args)

    con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with con:
        cur = con.cursor()
        sql = 'select card_name from card ' + sql2
        cur.execute(sql)
        print(cur.fetchall())


def filter_results(args):
    card_types = {
        'char': 'character',
        'upgr': 'upgrade',
        'event': 'event',
        'supp': 'support'
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
    card_id = input('Enter the card id or press enter to see card list: ')        
    response = requests.get(url + card_id)
    if response.status_code == 500:
        print('\nFilter choices: ' + str(args) + '\n')
        sql2 = filter_results(args)

        con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with con:
            cur = con.cursor()
            sql = 'select * from card ' + sql2
            cur.execute(sql)
            results = cur.fetchall()
            for result in results:
                display_info(result[-1], args, False)
    else:
        card = response.json()
        display_info(card, args)
        display_options(card, args, True)


def display_info(card, args, single):
    if single:
        print('\n' + card['name'])
        print('\tColor: ' + card['faction_code'])
        print('\tAffinity: ' + card['affiliation_name'])
        print('\tRarity: ' + card['rarity_name'])
        try:
            print('\tSides: ' + str(card['sides']))
        except KeyError:
            pass
        print('\tSet: ' + card['set_name'])
        if card['cost']: print('\tCost: ' + str(card['cost']))
        if card['health']: print('\tHealth: ' + str(card['health']))
        if card['points']: print('\tPoints: ' + str(card['points']))
        print('\tUnique: ' + str(card['is_unique']))
        if card['text']: 
            wrapped = textwrap.wrap('Text: \t' + card['text'])
            for i, wrap in enumerate(wrapped):
                if i != 0:
                    wrap = '\t' + wrap
                print('\t' + wrap)
    else:
        print(card['code'] + '\t' + card['set_code'] + '\t' +card['type_code'] + '    \t' + card['name'], end='')
        try:
            print('\t\tSides: ' + str(card['sides']))
        except KeyError:
            print()



def display_options(card, args):
    if card['type_code'] == 'character':
        option = input('\nEnter [i] to show card img, [p] for character pairings, ' +
            'or [s] to search another card:\n')
    else:
        option = input('\nEnter [i] to show card img or [s] to search another card:\n')
    
    if option not in 'isp':
        print('Not a valid option.')

    if option == 'i':
        show_card(card['set_code'], card['position'], card, args)
    elif option == 's':
        search(args)
    elif option == 'p' and card['type_code'] == 'character':
        find_pairings(card, args) 


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-t', dest='card_type', default='all', help='Limit card pool by card type ' +
        'Options: [all, char, supp, upgr, event, plot]\n') 
    parser.add_argument('-a', dest='affinity', default='hvn', help='Limit card pool by affinity. ' +
        'Options: [h(ero), v(illain), n(eutral)]\n' +
        '\tNote: May contain any combination of the options\n' +
        '\tex. -a vn\n \n')
    parser.add_argument('-c', dest='color', default='rgby', help='Limit card pool by color. ' +
        'Options: [g(ray), y(ellow), b(lue), r(ed)]\n' +
        '\tNote: May contain any combination of the options\n' +
        '\tex. -c rbg\n \n')
    parser.add_argument('-f', dest='t_format', default='std', help='Restrict card pool by format. Options: [inf, std, tri]')
    parser.add_argument('-s', dest='card_set', default='all', help='Restrict card pool by set. ' +
        'Options: [AW, SoR, EaW, TPS, LEG, RIV, WotF, AtG, CONV, AoN, SoH]\n \n')

    args = parser.parse_args()

    search(vars(args))


if __name__ == "__main__":
    main() 