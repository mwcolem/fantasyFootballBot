import os
import re
import time
from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
TEAM_URL_PART1 = "http://games.espn.com/ffl/clubhouse?leagueId=1172646&teamId="
TEAM_URL_PART2 = "&seasonId=2017"
TEAMS = {'coleman': 1, 'kyle': 2, 'isaac': 4, 'joey': 5,
    'bradley':3, 'clint': 12, 'morris': 9, 'ragan':13, 
    'laura': 7, 'frank': 10, 'gary': 11, 'mark': 8}

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def build_url(name):
    return TEAM_URL_PART1 + str(TEAMS.get(name)) + TEAM_URL_PART2

def get_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    return BeautifulSoup(page, "html.parser")

def handle_command(command, channel):
    response = "Not sure what you mean by " + command
    
    if command in TEAMS.keys():
        url = build_url(command)

        soup = get_soup(url)
        playerList = soup.find_all('td', attrs={'class':'playertablePlayerName'})
        players = []
        for row in playerList:
            players.append(row.find('a').getText())
        
        response = players

    elif re.match('scores', command):
        team_url = "http://games.espn.com/ffl/scoreboard?leagueId=1172646&seasonId=2017"
        soup = get_soup(team_url)
        teamList = soup.find_all('td', attrs={'class':'team'})
        scoreList = soup.find_all('td', attrs={'class':'score'})

        teams = []
        scores = []
        scoreOutput = []

        for row in teamList:
            teams.append(row.find('span', attrs={'class':'owners'}).getText())

        for row in scoreList:
            scores.append(row.getText())

        home = teams[0::2]
        homeScores = scores[0::2]
        away = teams[1::2]
        awayScores = scores[1::2]

        for i in range(len(home)):
            scoreOutput.append(home[i] + " vs " + away[i] + ": " + homeScores[i] + "/"+ awayScores[i])

        response = scoreOutput

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Fantasy football bot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
