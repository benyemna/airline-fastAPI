from dst_airlines_functions import get_token, create_search_dict_flight_offers, request_flight_offers, get_iata
from mongo_atlas_connection import *
import datetime

# Amadeus access
client_id_qmrt = "sBpJvjXswOMJsR4PPOsxdDU5v00o3ACA"
client_secret_qmrt = "sNpkAoobJ2NyUWDm"
 
token_tuple = get_token(client_id_qmrt, client_secret_qmrt)

# suppression de tous les enregistrements de la base de données
flight_offers_MRS_ATH_cron_collection.delete_many({})

# création liste des destinations et des dates à intégrer à la base de données
departure_cities = [["Marseille", "France"]]
departure_airport_iata_list = get_iata(departure_cities, iata_airportname_location_collection)

arrival_cities = [["Athens", "Greece"]]
arrival_airport_iata_list = get_iata(arrival_cities, iata_airportname_location_collection)

date_list = []
starting_date = datetime.date.today()
ending_date = starting_date + datetime.timedelta(days=90)
day = datetime.timedelta(days=1)

while starting_date <= ending_date:
    date_list.append(starting_date.strftime('%Y-%m-%d'))
    starting_date += day


# boucles pour requêter sur toutes les routes possibles entre les routes de départ et d'arrivée aux dates demandées et charger les données dans la base de données
for departure_airport in departure_airport_iata_list:
    for arrival_airport in arrival_airport_iata_list:
        if not departure_airport == arrival_airport:
            for route_date in date_list:
                dict_request = create_search_dict_flight_offers(originLocationCode = departure_airport, destinationLocationCode = arrival_airport, departureDate = route_date)
                dict_route = request_flight_offers(dict_request, token_tuple)
                dict_route["route_info"] = {"departure_airport_iata" : departure_airport, "arrival_airport_iata" : arrival_airport, "route_date" : route_date}
                flight_offers_MRS_ATH_cron_collection.insert_one(dict_route)