from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import credentials as cred

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