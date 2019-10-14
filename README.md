# NHL Daily Tracker
Track stats for NHL offensive players and compare them with players in your own league.

![Week 1 Dashboard](https://github.com/c-h-b-chen/nhl_daily_tracker/blob/master/nhl_dashboard.png)

I needed a way to visualize and interact with player performance over time for my fantasy hockey league that would take into account our own league point system. What this project ended up being (and I'm still working on it) consists of two scripts, a database, and Tableau.

Running hockeyscrape.py will pull the daily stats for all players (not counting Goalies) from hockey-reference.com and add a 'total' category that sums up all points based on your league settings. You can remove the logging in the script so that it can work as an AWS Lambda function to automate the process or just use as is with an EC2 isntance. This will then be uploaded to a table.

*Due to some inconsistent HTML formatting issues, I will be updating this script to use Selenium for more consistent scraping*

Authenticating hockeyteams.py with your OAuth2 credentials (you can register an app with the yahoo fantasy API) will allow you to access features from your league. I use this to keep an updated table with the entire league's roster for player comparison.

Tableau allows me to interact with each roster in my league to compare with available players to help with my trade decisions.

## Additional Work
In future iterations I plan on adding visualization to a player's future games and maybe some predictive analysis.
