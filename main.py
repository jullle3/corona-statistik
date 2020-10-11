import json

import requests
import pprint as pp
import os
from datetime import date, timedelta


url_infected_by_age_grp = "https://services5.arcgis.com/Hx7l9qUpAnKPyvNz/arcgis/rest/services/sygdomstilf_aldergrp_kom_new/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&groupByFieldsForStatistics=SampleAgeGrp&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Antal_pat%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&resultType=standard&cacheHint=true"
url_infected_by_kommune = "https://services5.arcgis.com/Hx7l9qUpAnKPyvNz/arcgis/rest/services/incidens_kort_saml/FeatureServer/0/query?f=json&where=NAVN%3C%3E%27Christians%C3%B8%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=incidens%20desc&resultOffset=0&resultRecordCount=100&resultType=standard&cacheHint=true"


def calc_newly_infected_by_age_grp(days_to_look_back=1):
    past_data_path = "infected_by_age_grp/" + str(date.today() - timedelta(days_to_look_back)) + ".json"
    todays_data_path = "infected_by_age_grp/" + str(date.today()) + ".json"

    if not os.path.exists(past_data_path):
        raise Exception(f"Lacking past data for date {date.today() - timedelta(days_to_look_back)}")
    past_data = json.loads(open(past_data_path).read())

    # Opret evt entry
    if not os.path.exists(todays_data_path):
        data = requests.get(url_infected_by_age_grp).json()
        open(todays_data_path, "w").write(json.dumps(data, indent=4))

    todays_data = json.loads(open(todays_data_path).read())
    strings = []
    total_new_infections = 0
    # Calc
    for age_grp_data in todays_data["features"]:
        todays_agr_grp = age_grp_data["attributes"]["SampleAgeGrp"]
        todays_infected = age_grp_data["attributes"]["value"]

        past_infected = next(e["attributes"]["value"] for e in past_data["features"] if e["attributes"]["SampleAgeGrp"] == todays_agr_grp)

        new_infections = todays_infected-past_infected
        strings.append({
            "string": f'{todays_agr_grp:<15} {new_infections:<15}',
            "new_infections": new_infections
            }
        )
        total_new_infections += new_infections

    print(len(strings))
    print(f'{total_new_infections=}')
    # Print. Printer her fordi vi skal bruge "total_new_infections" til at angive %
    print(f'{"Aldersgruppe":<15} {"Nye smittede":<15} i %')
    for s in strings:
        out = s["string"]
        if s["new_infections"] != 0:
            out = out + f'{round(s["new_infections"]/total_new_infections * 100, 2)}'
        print(out)
        

calc_newly_infected_by_age_grp(1)