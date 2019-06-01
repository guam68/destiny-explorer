import argparse
import requests
from PIL import Image
import json
import textwrap


def show_card(card_id):
    set_code = 'SWD16a_'
    card_num = 20
    url = 'http://lcg-cdn.fantasyflightgames.com/swd/' + set_code + str(card_num) + '.jpg'

    response = requests.get(url)
    with open('card_img.jpg', 'wb') as f:
        f.write(response.content)

    img = Image.open('card_img.jpg')
    img.show()


def find_pairings(card):
    pass


def search(args):
    url = 'https://swdestinydb.com/api/public/card/' 
    card_id = input('Enter the card id or press enter to see card list: ')        
    response = requests.get(url + card_id)
    if response.status_code == 500:
        # filter results by args
        print('fail')
    else:
        card = response.json()
        display_info(card, args)


def display_info(card, args):
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
    if card['type_code'] == 'character':
        option = input('\nEnter [i] to show card img, [p] for character pairings, ' +
            'or [s] to search another card:\n')
    else:
        option = input('\nEnter [i] to show card img or [s] to search another card:\n')
    
    if option not in 'isp':
        print('Not a valid option.')

    if option == 'i':
        show_card(card['set_code'], card['position'])
    elif option == 's':
        search(args)
    elif option == 'p' and card['type_code'] == 'character':
        find_pairings(card) 


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
        'Options: [awk, sor, eaw, 2ps, leg, riv, wotf, atg, conv]\n \n')

    args = parser.parse_args()

    search(vars(args))


if __name__ == "__main__":
    main() 