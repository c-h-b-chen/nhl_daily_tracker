import requests
import sys
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from sqlalchemy import create_engine
from sqlalchemy.types import BIGINT
from selenium import webdriver

USE_SELEN = False
DATABASE = 'mysql+pymysql://user:pass@hockey-1.cgk9rffkqlbn.us-east-1.rds.amazonaws.com/hockey?charset=utf8'


def chrome_scrape(urlstring, date):
    driver = webdriver.Chrome('../chromedriver')
    driver.get(urlstring)

    share_btn = driver.find_element_by_class_name('hasmore')
    share_btn.click()
    csv_btn = driver.find_element_by_xpath("//*[contains(text(),'Get table as CSV')]")
    csv_btn.click()
    csv = driver.find_element_by_id('csv_skaters').text

    df = pd.read_csv(pd.compat.StringIO(csv), header=1) # change header

    clean(df)

    # Rename the columns
    # Drop boxscore
    # Re Map
    # Convert type
    # 


def soup(urlstring, date):
    try:
        request = requests.get(urlstring)
    except Exception as diag:
        print('Bad URL string: ')
        print(urlstring)
        log = open('log.txt', 'a')
        log.write(str(diag.__class__.__name__) + ':' + str(diag))
        log.close()

    soup = BeautifulSoup(request.content, features="html5lib")
    players = soup.tbody.find_all('tr')

    records = []
    for player in players:
        stats = ['20' + date[2] + '-' + date[1] + '-' + date[1]]
        for data in player:
            stats.append(data.getText().split('\n')[0])
        records.append(stats)
    df = pd.DataFrame(data, columns=['date', 'rank', 'player', 'position', 'team', 'home', 'opp', 'win', 'boxscore', 'goals', 'assists', 'points', '+/-', 'pim', 'ev_goals',
                                     'pp_goals', 'sh_goals', 'gw_goals', 'ev_assists', 'pp_assists', 'sh_assists', 'sog', 'shoot%', 'shifts', 'toi', 'hit', 'blk', 'fow', 'fol', 'fo%'])
    clean(df)


def clean_df(df)
    df.drop(columns=['boxscore'], inplace=True)

    homemap = {'@': 0, '': 1, 'W': 1, 'L': 0}
    df['home'] = df['home'].map(homemap)
    df['win'] = df['win'].map(homemap)
    df.iloc[:, 7:23] = df.iloc[:, 7:23].apply(pd.to_numeric)
    df.iloc[:, 24:] = df.iloc[:, 24:].apply(pd.to_numeric)
    df[['date']] = df[['date']].apply(pd.to_datetime)
    df['rank'] = pd.to_numeric(df['rank'])

    df[['blk', 'hit', 'sog']] = df[['blk', 'hit', 'sog']].fillna(0)
    df['total'] = df.apply(lambda row: 3 * row['goals'] + 2 * (row['assists'] + row['sh_assists'] + row['sh_goals']) + .3 * (row['+/-'] + row['sog'] + row['hit']) + .5 * (row['pim'] + row['pp_goals'] + row['pp_assists'] + row['blk']), axis=1)

    return df

def scrape(date):
    urlstring = 'https://www.hockey-reference.com/friv/dailyleaders.fcgi?month=' + \
                date[0] + "&day=" + date[1] + "&year=20" + date[2]

    df = chrome_scrape(urlstring, date) if USE_SELEN else soup(urlstring, date)

    insert_db(df, table='daily')


def insert_db(df, table, exists='append', db=DATABASE):
    try:
        engine = create_engine(db, encoding='utf8')
        try:
            df.to_sql(table, con=engine, if_exists=exists)
        except Exception as diag:
            print(diag.__class__.__name__, ': Unable to insert into database')
            print(diag)
            log = open('log.txt', 'a')
            log.write(str(diag.__class__.__name__))
            log.write('\nUnable to insert into database')
            log.close()
    except Exception as diag:
        print(diag, ": Unable to connect to database")
        log = open('log.txt', 'a')
        log.write(str(diag.__class__.__name__) + ':' + str(diag))
        log.write('Unable to connect into database')
        log.close()


def main():

    log = open('log.txt', 'a')
    log.write('\n=======Scraping For=======\n' +
              str(datetime.datetime.today()) + '\n')
    log.close()

    x = datetime.datetime.today() - datetime.timedelta(1)
    date = x.strftime('%x').split('/')


    #To do
    try:
        elif len(sys.argv) == 4:
            date = sys.argv[1:]
        else:
        print('Bad input format')
        log = open('log.txt', 'a')
        log.write('Ban input format\nProgram aborted')
        log.close()
    log = open('log.txt', 'a')
    log.write('\n' + str(datetime.datetime.today()) +
              '\n======Program End======\n')
    log.close()


if __name__ == '__main__':
    main()
