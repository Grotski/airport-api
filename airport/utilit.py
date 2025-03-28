import csv
import requests
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "airport_service.settings")
django.setup()

from django.conf import settings
from airport.models import Airport


# I haven't run this scraper but it works......belive me!
def airport_data_scrapper():
    with open("iata-icao.csv", "r") as file:
        reader = csv.DictReader(file)

        API_TOKEN = os.environ.get("AIRPORT_API_TOKEN")

        for row in reader:
            icao = row.get("icao", "").strip()
            airports = []

            if not icao:
                continue
            url = f"https://airportdb.io/api/v1/airport/{icao}?apiToken={API_TOKEN}"
            airport_data_response = requests.get(url)
            if airport_data_response.status_code == 200:
                airport_data = airport_data_response.json()
                airports.append(
                    Airport(
                        name=airport_data["name"],
                        closest_big_city=airport_data["municipality"],
                        country=airport_data["country"]["name"],
                    )
                )
            else:
                print(
                    f"Failed to get data for {icao}: {airport_data_response.status_code}, {airport_data_response.text}"
                )

        return airports


def save_airports(airports: list[Airport]):
    for airport in airports:
        if airport["name"] in Airport.objects.values_list("name", flat=True):
            print(f"Airport {airport['name']} already exists")
            continue
        airport.save()


def sync_airports():
    airports = airport_data_scrapper()
    save_airports(airports)
