import requests
import sys
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from sqlalchemy import create_engine

DATABASE = 'mysql+pymysql://admin:hockeyhockey@hockey-1.cgk9rffkqlbn.us-east-1.rds.amazonaws.com/hockey?charset=utf8'


def scrape(date):
    urlstring = 'https://www.hockey-reference.com/friv/dailyleaders.fcgi?month=' + \
                date[0] + "&day=" + date[1] + "&year=20" + date[2]
    try:
        request = requests.get(urlstring)
    except Exception as diag:
        print('Bad URL string: ')
        print(urlstring)
        print(date[:])
        log = open('log.txt', 'a')
        log.write(str(diag.__class__.__name__) + ':' + str(diag))
        log.close()

    soup = BeautifulSoup(request.content, features="html5lib")
    players = soup.tbody.find_all('tr')
    day = []
    rank = []
    name = []
    pos = []
    team = []
    home = []
    opp = []
    win = []
    goals = []
    assists = []
    pts = []
    plusmin = []
    pim = []
    ev_g = []
    pp_g = []
    sh_g = []
    gw_g = []
    ev_a = []
    pp_a = []
    sh_a = []
    sog = []
    shoot_per = []
    shift = []
    toi = []
    hit = []
    blk = []
    fow = []
    fol = []
    fo_per = []
    total = []

    for player in players:
        stats = []
        for data in player:
            stats.append(data.getText().split('\n')[0])
        try:
            shoot_per.append(None) if stats[21] == "" else shoot_per.append(
                float(stats[21]))
            blk.append(None) if stats[25] == "" else blk.append(int(stats[25]))
            fow.append(None) if stats[26] == "" else fow.append(int(stats[26]))
            fol.append(None) if stats[27] == "" else fol.append(int(stats[27]))
            fo_per.append(None) if stats[28] == "" else fo_per.append(
                float(stats[28]))
        except Exception as diag:
            print(diag, ': Possible empty stat')
            log = open('log.txt', 'a')
            log.write(str(diag.__class__.__name__) + ':' + str(diag))
            log.write('* Possible Empty Stat *')
            log.close()

        #print(stats[8], stats[9], stats[19], stats[15], stats[11], stats[20], stats[24], stats[12], stats[14], stats[18], blk[-1], sep=' ')
        #print(stats[1])

        try:
            rank.append(int(stats[0]))
            goals.append(int(stats[8]))
            assists.append(int(stats[9]))
            pts.append(int(stats[10]))
            plusmin.append(int(stats[11]))
            pim.append(int(stats[12]))
            ev_g.append(int(stats[13]))
            pp_g.append(int(stats[14]))
            sh_g.append(int(stats[15]))
            gw_g.append(int(stats[16]))
            ev_a.append(int(stats[17]))
            pp_a.append(int(stats[18]))
            sh_a.append(int(stats[19]))
            sog.append(int(stats[20]))
            shift.append(int(stats[22]))
            min_sec = stats[23].split(':')
            toi_in_secs = int(min_sec[0]) * 60 + int(min_sec[1])
            toi.append(toi_in_secs)
            hit.append(int(stats[24]))
        except Exception as diag:
            print(diag, ': Possible bad int conversion')
            log = open('log.txt', 'a')
            log.write(str(diag.__class__.__name__) + ':' + str(diag))
            log.write('* Possible bad int conversion *')
            log.close()


        points = 3*goals[-1] + 2*(assists[-1] + sh_a[-1] + sh_g[-1]) + .3*(plusmin[-1] + sog[-1] + hit[-1]) + .5*(pim[-1]+ pp_g[-1] + pp_a[-1] + blk[-1])

        try:
            total.append(points)
            day.append(date[0] + '-' + date[1] + '-' + date[2])
            name.append(stats[1])
            pos.append(stats[2])
            team.append(stats[3])
            home.append(0) if stats[4] == '@' else home.append(1)
            opp.append(stats[5])
            win.append(1) if stats[6] == 'W' else win.append(0)
        except Exception as diag:
            print(diag, ': Cannot scrape bad data')
            log = open('log.txt', 'a')
            log.write(str(diag.__class__.__name__) + ':' + str(diag))
            log.write('* Cannot scrape bad data *')
            log.close()

    df = pd.DataFrame({
        "date": day,
        "rank": rank,
        "player": name,
        "position": pos,
        "team": team,
        "home": home,
        "opp": opp,
        "win": win,
        "goals": goals,
        "assists": assists,
        "points": pts,
        "+/-": plusmin,
        "pim": pim,
        "ev_goals": ev_g,
        "pp_goals": pp_g,
        "sh_goals": sh_g,
        "gw_goals": gw_g,
        "ev_assists": ev_a,
        "pp_assists": pp_a,
        "sh_assists": sh_a,
        "sog": sog,
        "shoot%": shoot_per,
        "shifts": shift,
        "toi": toi,
        "hit": hit,
        "blk": blk,
        "fow": fow,
        "fol": fol,
        "fo%": fo_per,
        "total": total})
    insert_db(df)

def insert_db(df, db=DATABASE):
    try:
        engine = create_engine(db, encoding='utf8')
        try:
            df.to_sql('daily', con=engine, if_exists='append')
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
    log.write('\n=======Scraping For=======\n' + str(datetime.datetime.today()) + '\n')
    log.close()
    if len(sys.argv) < 2:
        x = datetime.datetime.today() - datetime.timedelta(1)
        date = x.strftime('%x').split('/')
        scrape(date)
    elif len(sys.argv) == 4:
        scrape(sys.argv[1:])
    else:
        print('Bad input format')
        log = open('log.txt', 'a')
        log.write('Ban input format\nProgram aborted')
        log.close()
    log = open('log.txt', 'a')
    log.write('\n' + str(datetime.datetime.today()) + '\n======Program End======\n')
    log.close()


if __name__ == '__main__':
    main()
