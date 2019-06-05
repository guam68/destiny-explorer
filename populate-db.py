import requests
import json
import credentials as cred
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

url = 'https://swdestinydb.com/api/public/cards'


response = requests.get(url).json()

con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()

sql = """
    insert into card
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    on conflict do nothing;       
"""

for i, card in enumerate(response):
    print(i)
    subtypes = []
    try:
        sides = card['sides']
    except KeyError:
        sides = None
    try:
        for sub in card['subtypes']:
            subtypes.append(sub['name'])
    except KeyError:
        subtypes = None

    cur.execute(sql,(
        sides,
        card['set_code'],
        card['set_name'],
        card['type_code'],
        card['type_name'],
        card['faction_code'],
        card['faction_name'],
        card['affiliation_code'],
        card['affiliation_name'],
        card['rarity_code'],
        card['rarity_name'],
        card['position'],
        card['code'],
        card['ttscardid'],
        card['name'],
        card['subtitle'],
        card['cost'],
        card['health'],
        card['points'],
        card['text'],
        card['deck_limit'],
        card['flavor'],
        card['illustrator'],
        card['is_unique'],
        card['has_die'],
        card['has_errata'],
        card['url'],
        card['imagesrc'],
        card['label'],
        card['cp'],
        subtypes)
    ) 
