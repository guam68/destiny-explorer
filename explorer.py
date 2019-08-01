import copy
import json
import textwrap

from colorama import Fore, Style
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import card_options as card_opt
import credentials as cred
import requests


class Explorer:
    def __init__(self, args):
        self.args = args


    def space_adj(self, string):
        if len(string) < 20:
            while len(string) < 20:
                string = string + ' '
        return string[0:19]


    def display_options(self, card):
        proxy = '[x] to find a proxy die, ' if card['has_die'] else ' '
        if card['type_code'] == 'character':
            option = input('\nEnter [i] to show card img, [p] for character pairings, ' +
                '[f] to change filters, ' + proxy + 'or [s] to search another card:\n')
        else:
            option = input('\nEnter [i] to show card img, ' + proxy + 'or [s] to search another card:\n')
        
        if option not in 'ispfx':
            self.search()

        if option == 'i':
            card_opt.show_card(card['set_code'], card['position'], card, self.args)
            self.display_options(card)
        elif option == 's':
            self.search()
        elif option == 'p' and card['type_code'] == 'character':
            card_opt.find_pairings(self, card, self.args) 
        elif option == 'f':
            self.change_filters()
        elif option == 'x':
            card_opt.get_proxy_dice(card) 
            self.display_options(card)

    
    def change_filters(self):
        flag = False
        filters = {
            't': 'card_type',
            'a': 'affinity',
            'c': 'color',
            'f': 't_format',
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
            _filter = input('[t]ype, [a]ffinity, [c]olor, [f]ormat, [s]et, [enter] to reset: ')
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
                    self.args[filters[_filter]] = option 
                elif option in filter_options[_filter][1]:
                    self.args[filters[_filter]] = option 
            elif _filter == '':
                self.args['card_type'] = 'all'
                self.args['affinity'] = 'hvn'
                self.args['color'] = 'rgby'
                self.args['t_format'] = 'std'
                self.args['card_set'] = 'all'
                print('Filters reset\n')

            cont = input('[r] to return to search or [enter] to change another filter: ')
            
            flag = True if cont == 'r' else False
        
        self.search()


    def filter_results(self, is_pairing):
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

        if self.args['card_set'] == 'all':
            if self.args['t_format'] == 'std':
                sql2 = '''
                    where set_code in ('SoH', 'AoN', 'CONV', 'AtG', 'WotF', 'LEG', 'TPG', 'RIV') 
                '''
            elif self.args['t_format'] == 'tri':
                sql2 = '''
                    where set_code in ('SoH', 'AoN', 'CONV') 
                '''
            else:
                sql2 = 'where deck_limit > 0' 
        else:
            sql2 = 'where set_code = \'' + self.args["card_set"] + '\''

        if is_pairing:
            return sql2

        if self.args['card_type'] != 'all':
            sql2 += ' and type_code = \'' + card_types[self.args['card_type']] + '\''

        card_colors = []
        for color in colors.keys():
            if color in self.args['color']:
                card_colors.append(colors[color])
        card_colors = 'in ' + str(tuple(card_colors)) if len(card_colors) > 1 else '= \'' + card_colors[0] + '\''
        sql2 += ' and faction_code ' + card_colors

        affin = []
        for aff in affinities.keys():
            if aff in self.args['affinity']:
                affin.append(affinities[aff])
        card_aff = 'in ' + str(tuple(affin)) if len(affin) > 1 else '= \'' + affin[0] + '\''
        sql2 += ' and affiliation_code ' + card_aff

        return sql2


    def search(self):
        url = 'https://swdestinydb.com/api/public/card/' 
        card_id = input('\nEnter the card id or [enter] to see card list ([a] for adv search, ' +
            '[q] to quit, [f] to change filters): ')
        if card_id == 'q':
            raise SystemExit
        elif card_id == 'f':
            self.change_filters()
        elif card_id == 'a':
            self.adv_search()
        else:
            response = requests.get(url + card_id)
            if response.status_code == 500:
                print('\nFilter choices: ' + str(self.args) + '\n')
                sql2 = self.filter_results(False)

                con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
                con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

                with con:
                    cur = con.cursor()
                    sql = 'select * from card ' + sql2
                    cur.execute(sql)
                    results = cur.fetchall()
                    for result in results:
                        self.display_info(result[-1], False)
                    print()
                    self.search()
                    
            else:
                card = response.json()
                self.display_info(card, True)
                self.display_options(card)


    def adv_search(self):
        choice = input('\n[t] to search by card text or [enter] to search by card name: ')
        in_text = 'Enter text keyword: ' if choice == 't' else 'Enter card name: '
        sql1 = ' and card_text' if choice == 't' else ' and card_name'
        sql2 = self.filter_results(False)
        keyword = '%' + input(in_text) + '%'

        con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with con:
            cur = con.cursor()
            sql = ("select * from card " + sql2 + sql1 + " ilike '" + keyword + "'")
            cur.execute(sql)
            cards = cur.fetchall()
        
        for card in cards:
            self.display_info(card[-1], False)

        self.search()


    def display_info(self, card, single):
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
                card['type_code'] + '    \t' + txt_colors[card['faction_code']] + self.space_adj(card['name']) + reset, end='')
            try:
                print('\tSides: ' + str(card['sides']) + reset)
            except KeyError:
                print()
