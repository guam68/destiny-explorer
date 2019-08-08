import requests
import json
import credentials as cred
from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class DBManager:
    def __init__(self):
        self.url = 'https://swdestinydb.com/api/public/cards'
        self.response = []


    def run(self):
        choice = input('\n[Enter] to continue or any key for database check: ')
        if choice != '':
            db_manager = DBManager()
            db_manager.check_for_db()

    def check_for_db(self):
        print('Checking for database...')
        con = connect(dbname='destiny', user=cred.login['user'], host='localhost', password=cred.login['password'])
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        try:
            cur.execute("select count(*) from card;")
            count = cur.fetchone()
            self.check_for_update(count[0], con)
        except Exception:
            self.create_table(con)
            

    def create_table(self, con):
        print('Creating table...')
        cur = con.cursor()
        sql = """
            create table card(
                sides text,
                set_code text,
                set_name text,
                type_code text,
                type_name text,
                faction_code text,
                faction_name text,
                affiliation_code text,
                affiliation_name text,
                rarity_code text,
                rarity_name text,
                card_num smallint,
                code text primary key,
                ttscardid text,
                card_name text,
                subtitle text,
                card_cost smallint,
                health smallint,
                points text,
                card_text text,
                deck_limit smallint,
                flavor text,
                illustrator text,
                is_unique boolean,
                has_die boolean,
                has_errata boolean,
                url text,
                imagesrc text,
                card_label text,
                cp smallint,
                subtypes text[],
                obj jsonb
            );
        """
        cur.execute(sql)
        self.check_for_update(0, con)


    def check_for_update(self, count, con):
        print('Checking for updates...')
        self.response = requests.get(self.url).json()
        
        if len(self.response) == count:
            print('Database up to date.\n')
            con.close()
        else:
            self.populate_db(con)


    def populate_db(self, con):
        print('Populating database...')
        count = 0
        cur = con.cursor()
        sql = """
            insert into card
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict do nothing;       
        """

        for card in enumerate(self.response):
            count += 1
            subtypes = []
            card = card[1]
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
                subtypes,
                json.dumps(card))
            ) 

        con.close()
        print(str(count) + ' cards in database')


if __name__ == '__main__':
    db_manager = DBManager()
    db_manager.check_for_db()