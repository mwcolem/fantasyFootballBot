from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    return BeautifulSoup(page, "html5lib")

def get_team():
    team_url = "http://games.espn.com/ffl/clubhouse?leagueId=1172646&teamId=1&seasonId=2017"
    soup = get_soup(team_url)
    playerList = soup.find_all('td', attrs={'class':'playertablePlayerName'})
    players = []

    for row in playerList:
        players.append(row.find('a').getText())
    
    return players

team = get_team()
print(team)