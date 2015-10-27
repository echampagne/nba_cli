#!/usr/bin/env
from setuptools import setup

setup(
	name='nba_cli',
	version='0.0.0.1',
	description="CLI for NBA games",
	author='Eric Champagne',
	author_email='echampagne27@gmail.com',
	keywords = 'nba basketball scores cli',
	url='https://github.com/echampagne/nba_cli',
	scripts=['nba.py', 'constants.py'],
	install_requires=[
		"click==5.0",
		"requests==2.7.0",
	],
	entry_points = {
		'console_scripts': [
			'nba = nba:main'
		],
	}
)