import requests
import sys
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


USE_SELEN = False
LOG = '../nhl_log.txt'
USER, PWD = open('../nhlcreds.txt', 'r').readlines()
DATABASE = 'mysql+pymysql://' + USER.strip() + ':' + PWD.strip() + '@hockey-1.cgk9rffkqlbn.us-east-1.rds.amazonaws.com/hockey?charset=utf8'
BASE_URL = 'https://www.hockey-reference.com/friv/dailyleaders.fcgi?month='


def chrome_scrape(urlstring, date):
    driver = webdriver.Chrome('../chromedriver')
    driver.get(urlstring)

    share_btn = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Share & more')]")))
    share_btn.click()

    csv_btn = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Get table as CSV')]")))

    # csv_btn = driver.find_element_by_xpath(
    #     "//*[contains(text(),'Get table as CSV')]")
    csv_btn.click()
    csv = driver.find_element_by_id('csv_skaters').text
    driver.quit()

    df = pd.read_csv(pd.compat.StringIO(csv), header=1, names=['rank', 'player', 'position', 'team', 'home', 'opp', 'win', 'boxscore', 'goals', 'assists', 'points', '+/-', 'pim', 'ev_goals',
                                                               'pp_goals', 'sh_goals', 'gw_goals', 'ev_assists', 'pp_assists', 'sh_assists', 'sog', 'shoot%', 'shifts', 'toi', 'hit', 'blk', 'fow', 'fol', 'fo%'])
    df['player'] = df['player'].str.split('\\').str[0]
    df.insert(loc=0, column='date', value='20' + date[2] + '-' + date[0] + '-' + date[1])

    return clean(df)


def soup(urlstring, date):
    try:
        request = requests.get(urlstring)
    except Exception as diag:
        print('Bad URL string: ')
        print(urlstring)
        log = open(LOG, 'a')
        log.write(str(diag.__class__.__name__) + ':' + str(diag))
        log.close()

    soup = BeautifulSoup(request.content, features="html5lib")
    players = soup.tbody.find_all('tr')

    records = []
    for player in players:
        stats = ['20' + date[2] + '-' + date[0] + '-' + date[1]]
        for data in player:
            stats.append(data.getText().split('\n')[0])
        records.append(stats)
    df = pd.DataFrame(records, columns=['date', 'rank', 'player', 'position', 'team', 'home', 'opp', 'win', 'boxscore', 'goals', 'assists', 'points', '+/-', 'pim', 'ev_goals',
                                        'pp_goals', 'sh_goals', 'gw_goals', 'ev_assists', 'pp_assists', 'sh_assists', 'sog', 'shoot%', 'shifts', 'toi', 'hit', 'blk', 'fow', 'fol', 'fo%'])
    return clean(df)


def clean(df):
    df.drop(columns=['boxscore'], inplace=True)

    homemap = {'@': 0, '': 1, None: 1}
    df['home'] = df['home'].map(homemap)

    def soi(toi):
        minutes, seconds = toi.split(':')
        return int(minutes) * 60 + int(seconds)
    df['toi'] = df['toi'].apply(lambda x: soi(x))
    df.iloc[:, 8:] = df.iloc[:, 8:].apply(pd.to_numeric)
    #df[['date']] = df[['date']].apply(pd.to_datetime)
    df['rank'] = pd.to_numeric(df['rank'])

    df[['blk', 'hit', 'sog']] = df[['blk', 'hit', 'sog']].fillna(0)
    df['total'] = df.apply(lambda row: 3 * row['goals'] + 2 * (row['assists'] + row['sh_assists'] + row['sh_goals']) + .3 * (
        row['+/-'] + row['sog'] + row['hit']) + .5 * (row['pim'] + row['pp_goals'] + row['pp_assists'] + row['blk']), axis=1)

    insert_db(df, table='daily')


def insert_db(df, table, exists='append', db=DATABASE):
    try:
        engine = create_engine(db, encoding='utf8')
        try:
            df.to_sql(table, con=engine, if_exists=exists, index=False)
        except Exception as diag:
            print(diag.__class__.__name__, ': Unable to insert into database')
            print(diag)
            log = open(LOG, 'a')
            log.write(str(diag.__class__.__name__))
            log.write('\nUnable to insert into database')
            log.close()
    except Exception as diag:
        print(diag, ": Unable to connect to database")
        log = open(LOG, 'a')
        log.write(str(diag.__class__.__name__) + ':' + str(diag))
        log.write('Unable to connect into database')
        log.close()


def main():

    log = open(LOG, 'a')
    log.write('\n=======Scraping For=======\n' +
              str(datetime.datetime.today()) + '\n')
    log.close()

    x = datetime.datetime.today() - datetime.timedelta(1)
    entry_date = x.strftime('%x').split('/')

    if len(sys.argv) == 4:
        entry_date = sys.argv[1:]

    # for i in range(2, 23):
        # entry_date = ['10', '0' + str(i), '19'] if i < 10 else ['10', str(i), '19']
        # urlstring = BASE_URL + entry_date[0] + "&day=" + \
        #     entry_date[1] + "&year=20" + entry_date[2]
        # print('Entry for ', entry_date)
        # chrome_scrape(urlstring, entry_date) if USE_SELEN else soup(urlstring, entry_date)

    urlstring = BASE_URL + entry_date[0] + "&day=" + \
        entry_date[1] + "&year=20" + entry_date[2]
    chrome_scrape(urlstring, entry_date) if USE_SELEN else soup(urlstring, entry_date)

    log = open(LOG, 'a')
    log.write('\n' + str(datetime.datetime.today()) +
              '\n======Program End======\n')
    log.close()


if __name__ == '__main__':
    main()
