from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import credentials as cred

def get_proxy_dice(base_card):
    proxies = []
    con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with con:
        cur = con.cursor()
        sql = ("select * from card where has_die = 'True'" )
        cur.execute(sql)
        cards = cur.fetchall()

    for card in cards:
        card_dict = dict(card[-1])
        if card_dict['sides'] == base_card['sides']:
            if base_card['name'] != card_dict['name']:
                proxies.append([card_dict['name'], card_dict['code']])
    
    if proxies:
        for proxy in proxies:
            print(proxy)
    else:
        print('No proxy dice found')