from yahoo_oauth import OAuth2
from hockeyscrape import insert_db
import yahoo_fantasy_api as yfa
import pandas as pd


def fill_tables(sc):
    gm = yfa.Game(sc, 'nhl')
    lg = gm.to_league(gm.league_ids(year=2019)[0])
    dummies = lg.teams()
    table_df = pd.DataFrame()

    # cleaning names for valid table entry
    for team in dummies:
        team['name'] = team['name'].replace(" ", "_")
        roster = lg.to_team(team['team_key']).roster()
        df = pd.DataFrame(roster)
        df['owner'] = team['name']
        df['team_key'] = team['team_key']
        df['position'] = df['eligible_positions'].apply('/'.join)
        df.drop(['eligible_positions'], inplace=True, axis=1)
        table_df = table_df.append(df, ignore_index=True)

    insert_db(table_df, 'league', 'replace')


oauth = OAuth2(None, None, from_file='../oauth2.json')
if not oauth.token_is_valid():
    oauth.refresh_access_token()

fill_tables(oauth)
