#!/bin/python
# Script to download the team logos
import os
import math
import requests
import json
from PIL import Image
from click import option, command

@command()
@option("-l", "--league", envvar="LEAGUE", default="bel")
@option("-f", "--force", is_flag=True)

def get_logos(league, force):
    # Vars
    API_URL = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}.1/teams"
    teams = requests.get(API_URL).json().get("sports")[0].get("leagues")[0].get("teams")

    # Create dir for league if not exist
    os.makedirs(f"assets/logos/{league}", exist_ok=True)
    logos_path = f"assets/logos/{league}/"

    # Download logo for every team
    for team in teams:
        team_name = team['team']['abbreviation']
        logo_len  = len(team['team']['logos'])
        logo_dest = f"{logos_path}/{team_name}.png"

        if logo_len > 0:
            logo_location = team['team']['logos'][0]['href']
            logo_response = requests.get(logo_location)

            if os.path.exists(logo_dest) and not force:
                print(f"Logo for {team_name} already exists, skipping...")
                continue  # Skip to next team
            
            try:
                print(f"Downloading logo for {team_name}...")
                with open(logo_dest, 'wb') as file:
                    file.write(logo_response.content)
                print(f"Download complete.")

            except requests.RequestException as e:
                print(f"Failed to download: {e}")

        else:
            print(f"Downloading logo for {team_name}...")
            print(f"Logo not found.")

if __name__ == '__main__':
    get_logos()