import os
import time
from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
TEAM_URL_PART1="http://games.espn.com/ffl/clubhouse?leagueId=1172646&teamId="
TEAM_URL_PART2="&seasonId=2017"
TEAMS={'coleman': 1, 'kyle': 2, 'isaac': 4, 'joey': 5, 'bradley':3, 'clint': 12, 'morris': 9, 'ragan':13, 'laura': 7, 'frank': 10, 'gary': 11, 'mark': 8}

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def build_url(name):
    return TEAM_URL_PART1 + TEAMS.get(name) + TEAM_URL_PART2

def get_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    return BeautifulSoup(page, "html5lib")

def handle_command(command, channel):
    response = "Not sure what you mean by " + command
    
    if (TEAMS.has_key(command)):
        url = build_url(command)

        soup = get_soup(url)
        playerList = soup.find_all('td', attrs={'class':'playertablePlayerName'})
        players = []
        for row in playerList:
            players.append(row.find('a').getText())
        
        response = players

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
        print("Axis and Allies Bot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
