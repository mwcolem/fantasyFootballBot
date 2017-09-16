from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    return BeautifulSoup(page, "html5lib")

team_url = "http://games.espn.com/ffl/scoreboard?leagueId=1172646&seasonId=2017"
soup = get_soup(team_url)
teamList = soup.find_all('td', attrs={'class':'team'})
scoreList = soup.find_all('td', attrs={'class':'score'})

teams = []
scores = []

for row in teamList:
    teams.append(row.find('span', attrs={'class':'owners'}).getText())

for row in scoreList:
    scores.append(row.getText())

home = teams[0::2]
homeScores = scores[0::2]
away = teams[1::2]
awayScores = scores[1::2]

for i in range(len(home)):
    print (home[i] + " vs " + away[i] + ": " + homeScores[i] + "/"+ awayScores[i])
