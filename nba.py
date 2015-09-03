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
	if conference.lower() == 'east':
		print_standings(res_json['resultSets'][4]['rowSet'])
	else:
		print_standings(res_json['resultSets'][5]['rowSet'])

def print_standings(standings):
	# Sort by win percentage to display
	standings.sort(key=lambda x: x[9], reverse=True)
	click.secho("{pos:6} {team:15} {wins:10} {losses:10} {winpercent:10}".format(
			pos="#", team="TEAM", wins="WINS", losses="LOSSES", winpercent="WIN PCT"
		), bold=True)
	for index, team in enumerate(standings, start=1):
		# secho is styled echo, fg='green' for example
		if index < 9:
			click.secho("{pos:6} {team:15} {wins:10} {losses:10} {winpercent:10}".format(
				pos=str(index), team=str(team[5]), wins=str(team[7]), losses=str(team[8]), winpercent=str(team[9])
			), fg="green")
		else:
			click.secho("{pos:6} {team:15} {wins:10} {losses:10} {winpercent:10}".format(
				pos=str(index), team=str(team[5]), wins=str(team[7]), losses=str(team[8]), winpercent=str(team[9])
			), fg="blue")
		# print "Team: %s \t W: %s \t L: %s" % (team[5], team[7], team[8])


# Set up command line arguments
@click.command()
@click.option('--standings', '-s', is_flag=True, help="Standing for a conference")
@click.option('--conference', '-c', type=click.Choice(['East', 'West', 'east', 'west']),
	help = (
		"Choose a conference, East or West"
	)
)

def main(standings, conference):
	'''
	Command line interface for the NBA
	'''
	if standings and conference:
		get_standings(conference=conference)
		return;
	if standings:
		get_standings()
		return

if __name__ == '__main__':
	main()