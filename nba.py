#!/usr/bin/env python

import requests
import click
import json
from datetime import datetime
from constants import League

TODAY = datetime.today()
CURRENT_SEASON = '2015-16'
BASE_URL = 'http://stats.nba.com/stats/{endpoint}/'

def get_json(endpoint, params):
	res = requests.get(BASE_URL.format(endpoint=endpoint), params=params)
	print res.url
	res.raise_for_status()
	return res.json()

def get_standings(month=TODAY.month, 
				   day=TODAY.day, 
				   year=TODAY.year,
				   league_id=League.NBA,
				   offset=0,
				   conference='east'):
	game_date = '{month:02d}/{day:02d}/{year}'.format(month=month,
													day=day,
													year=year)
	res_json = get_json(endpoint='scoreboard', params={'LeagueID': league_id,
													'GameDate': game_date,
													'DayOffset': offset})
	# print json.dumps(res_json['resultSets'][4]['rowSet'], indent=2)
	# print json.dumps(res_json['resultSets'][4]['headers'], indent=2)
	if conference.lower() == 'east':
		print_standings(res_json['resultSets'][4]['rowSet'])
	else:
		print_standings(res_json['resultSets'][5]['rowSet'])

def print_standings(standings):
	for team in standings:
		print "Team: %s \t W: %s \t L: %s" % (team[5], team[7], team[8])

@click.command()
@click.option('--standings', is_flag=True, help="Standing for a conference")
@click.option('--conference', type=click.Choice(['East', 'West', 'east', 'west']),
	help = (
		"Choose a conference, East or West"
	)
)

def main(standings, conference):
	if standings and conference:
		get_standings(conference=conference)
		return;
	if standings:
		get_standings()
		return

if __name__ == '__main__':
	main()