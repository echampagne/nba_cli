'''
    This module provides the syntax and methods
    to get NBA statistics from the command line.
'''

import requests
import click
from datetime import datetime
from constants import League

TODAY = datetime.today()
CURRENT_SEASON = '2015-16'
BASE_URL = 'http://stats.nba.com/stats/{endpoint}/'

def get_json(endpoint, params):
    '''
        Helper method for hitting some endpoint,
        and returning the result.
    '''
    res = requests.get(BASE_URL.format(endpoint=endpoint), params=params)
    res.raise_for_status()
    return res.json()

def get_standings(
        month=TODAY.month,
        day=TODAY.day,
        year=TODAY.year,
        league_id=League.NBA,
        offset=0,
        conference='all'):
    '''
        This method returns the east, west, or entire leagues standings
        for any given day. If no day is given, it gives the current day's
        standings.
    '''
    game_date = '{month:02d}/{day:02d}/{year}'.format(month=month,
                                                      day=day,
                                                      year=year)
    res_json = get_json(endpoint='scoreboard',
                        params={'LeagueID': league_id,
                                'GameDate': game_date,
                                'DayOffset': offset})

    if conference.lower() == 'east':
        print_standings(res_json['resultSets'][4]['rowSet'])
    elif conference.lower() == 'west':
        print_standings(res_json['resultSets'][5]['rowSet'])
    elif conference.lower() == 'all':
        east_standings = res_json['resultSets'][4]['rowSet']
        west_standings = res_json['resultSets'][5]['rowSet']
        # Merge the two lists into one,
        # Note that this works since the lists are the same size.
        all_standings = [
            item
            for pair in zip(east_standings, west_standings)
            for item in pair]
        print_standings(all_standings)


def print_standings(standings):
    '''
        This method formats and prints the standings.
    '''
    # Sort by win percentage to display
    standings.sort(key=lambda x: x[9], reverse=True)
    click.secho(
        "{pos:6} {team:15} {wins:10} {losses:10} "
        "{winpercent:10}"
        .format(pos="#", team="TEAM", wins="WINS",
                losses="LOSSES", winpercent="WIN PCT"),
        bold=True)

    for index, team in enumerate(standings, start=1):
    # secho is styled echo, fg='green' for example
        if index < 9:
            click.secho(
                "{pos:6} {team:15} {wins:10} {losses:10} {winpercent:10}"
                .format(pos=str(index), team=str(team[5]), wins=str(team[7]),
                        losses=str(team[8]), winpercent=str(team[9])),
                fg="green")
        else:
            click.secho(
                "{pos:6} {team:15} {wins:10} {losses:10} {winpercent:10}"
                .format(pos=str(index), team=str(team[5]), wins=str(team[7]),
                        losses=str(team[8]), winpercent=str(team[9])),
                fg="blue")


def get_games(
        month=TODAY.month,
        day=TODAY.day,
        year=TODAY.year,
        league_id=League.NBA,
        offset=0):
    '''
        Given a specific day this method
        get's the data for that day's NBA games.
    '''
    game_date = "{month:02d}/{day:02d}/{year}".format(month=month,
                                                      day=day,
                                                      year=year)
    res_json = get_json(endpoint='scoreboard',
                        params={'LeagueID': league_id,
                                'GameDate': game_date,
                                'DayOffset': offset})

    print_games(res_json['resultSets'][1]['rowSet'],
                res_json['resultSets'][0]['rowSet'])

def print_games(games, game_data):
    '''
        This method formats and displays a list of games.
    '''
    games_list = []
    # Construct a list of games from the JSON.
    for game, i in zip(games, xrange(0, len(games), 2)):
        games_list.append({'away': games[i],
                           'home': games[i+1]})
    for game, i in zip(game_data, xrange(0, len(games_list), 1)):
        games_list[i]['data'] = game

    for game in games_list:

        # Print team names in the game.
        click.secho(
            "{away_abv:3} ({away_record}) at {home_abv:3} ({home_record})"
            .format(away_abv=str(game['away'][4]),
                    home_abv=str(game['home'][4]),
                    away_record="".join(str(game['away'][6])),
                    home_record="".join(str(game['home'][6]))),
            bold=True)

        # Status of 1 indicates it hasn't started. So do not print score.
        if game['data'][3] == 1:
            start_time = game['data'][4]
            tv = game['data'][11]
            header_str = " "*3 + "Starts at {time:8}".format(time=str(start_time))
            if tv is not None:
                header_str += " on {tv:12}".format(tv=str(tv))
            click.secho(header_str, fg="blue")


        # Status of 2 indicates the game is in progress.
        if game['data'][3] == 2:
            click.secho("Game is in progress...")


        # Status of 3 indicates the game is over.
        if game['data'][3] == 3:
            # Count number of OTs in game and construct period header string
            num_ots = 0
            for i in xrange(11, 21):
                if game['home'][i] != 0:
                    num_ots += 1
            period_header = " "*5 + "Q1  Q2  Q3  Q4"
            for i in xrange(1, num_ots+1, 1):
                period_header += "  OT"+ str(i)
            period_header += "  Final"

            # Construct score string's
            away_score_str = " {away_abv:4}".format(away_abv=str(game['away'][4]))
            home_score_str = " {home_abv:4}".format(home_abv=str(game['home'][4]))
            away_final_score = 0
            home_final_score = 0
            for i in xrange(7, 11+num_ots,1):
                away_score_str += "{score:4}".format(score=str(game['away'][i]))
                home_score_str += "{score:4}".format(score=str(game['home'][i]))
                away_final_score += game['away'][i]
                home_final_score += game['home'][i]
            away_score_str += "{final_score:4}".format(final_score=str(away_final_score))
            home_score_str += "{final_score:4}".format(final_score=str(home_final_score))

            click.secho(period_header, bold=True, fg="blue")
            click.secho(away_score_str + "\n" + home_score_str)

# Set up command line arguments
@click.command()
@click.option('--standings', is_flag=True, help="Standing for a conference")
@click.option('--conference',
              type=click.Choice(['East', 'West', 'east', 'west']),
              help=("Choose a conference, East or West"))
@click.option('--live', is_flag=True, help="Get live game scores.")


def main(standings=None, conference=None, live=None):
    '''
        Command line interface for the NBA
    '''
    if standings and conference:
        get_standings(conference=conference)
        return
    if standings:
        get_standings()
        return
    if live:
        get_games()
        return

if __name__ == '__main__':
    main()
