from yahoo_oauth import OAuth2
from hockeyscrape import insert_db
import yahoo_fantasy_api as yfa
import pandas as pd

#Authenticate -> game -> league -> team
#Insert
#
#

def login():
    oauth = OAuth2(None, None, from_file='oauth2.json')
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

def create_table(tablename, df):

def 