import requests
import json
import time
from pymongo import MongoClient
import re


def get_token(client_id, client_secret, url_token = "https://test.api.amadeus.com/v1/security/oauth2/token", grant_type = "client_credentials"):
    """
    Fonction qui à partir de nos credentials va aller chercher le token qui nous permettra d'utiliser l'API Lufthansa
    Paramètres ;
        client_id : l'id de notre account
        client_secret : le secret de notre account
        url_token : url où aller chercher le token, par défaut : "https://test.api.amadeus.com/v1/security/oauth2/token"
        grant_type : le paramètre grant_type de la requête poeur obtenir le token, par défaut "client_credentials"
    Return :
        tuple contenant :
            access_token : le token nécessaire à l'accès aux requêtes
            token_expire_time : la durée de validité en seconde du token
            t_token_import : le t où on a importé le token pour avoir une référence quant à la validité du token
            client_id : l'id de notre account
            client_secret : le secret de notre account
    """
    t_token_import = time.time()
    token = requests.post(url_token, data= {"client_id" : client_id, "client_secret" : client_secret, "grant_type" : grant_type})
    token_json = json.loads(token.content)
    access_token = token_json["access_token"]
    token_expire_time = token_json["expires_in"]
    return access_token, token_expire_time, t_token_import, client_id, client_secret


def is_token_expired(token_tuple):
    """
    La fonction test si le token est expiré
    Paramètres :
        token_tuple : tuple issu de la fonction get_token
    Return :
        boolean : True si le token est expiré, False sinon
    """
    res = False
    if time.time()-token_tuple[2] > token_tuple[1]:
        res = True
    return res
        

def create_search_dict_flight_offers(originLocationCode, destinationLocationCode, departureDate, adults = "1",
                    returnDate="", children="", infants="", travelClass="", includedAirlineCodes="",
                    excludedAirlineCodes="", nonStop ="", currencyCode="EUR", maxPrice="", max=""):
    """
    Fonction qui permet d'effectuer de créer le dictionnaire de paramétrage de la requête "flight offers" de l'API Amadeus
    Paramètres :
        originLocationCode : city/airport IATA code from which the traveler will depart, e.g. BOS for Boston
        destinationLocationCode : city/airport IATA code to which the traveler is going, e.g. PAR for Paris
        departureDate : the date on which the traveler will depart from the origin to go to the destination. Dates are specified in the ISO 8601 YYYY-MM-DD format, e.g. 2017-12-25
        adults : the number of adult travelers (age 12 or older on date of departure) ; Default value : 1
        returnDate (optionnel) : the date on which the traveler will depart from the destination to return to the origin. If this parameter is not specified, only one-way itineraries are found. If this parameter is specified, only round-trip itineraries are found. Dates are specified in the ISO 8601 YYYY-MM-DD format, e.g. 2018-02-28
        children (optionnel) : the number of child travelers (older than age 2 and younger than age 12 on date of departure) who will each have their own separate seat. If specified, this number should be greater than or equal to 0
        infants (optionnel) : the number of infant travelers (whose age is less or equal to 2 on date of departure). Infants travel on the lap of an adult traveler, and thus the number of infants must not exceed the number of adults. If specified, this number should be greater than or equal to 0
        travelClass (optionnel) : most of the flight time should be spent in a cabin of this quality or higher. The accepted travel class is economy, premium economy, business or first class. If no travel class is specified, the search considers any travel class ; Available values : ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
        includedAirlineCodes (optionnel) : This option ensures that the system will only consider these airlines. This can not be cumulated with parameter excludedAirlineCodes ; Airlines are specified as IATA airline codes and are comma-separated, e.g. 6X,7X,8X
        excludedAirlineCodes (optionnel) : This option ensures that the system will ignore these airlines. This can not be cumulated with parameter includedAirlineCodes ; Airlines are specified as IATA airline codes and are comma-separated, e.g. 6X,7X,8X
        nonStop (optionnel) : if set to true, the search will find only flights going from the origin to the destination with no stop in between ; Default value : false
        currencyCode (optionnel) : the preferred currency for the flight offers. Currency is specified in the ISO 4217 format, e.g. EUR for Euro
        maxPrice (optionnel) : maximum price per traveler. By default, no limit is applied. If specified, the value should be a positive number with no decimals
        max (optionnel) : maximum number of flight offers to return. If specified, the value should be greater than or equal to 1 ; Default value : 250
    Return:
        le dictionnaire à utiliser dans la fonction request_flight_offers
    """
    return {"originLocationCode": originLocationCode, "destinationLocationCode": destinationLocationCode, 
        "departureDate": departureDate, "adults": adults, "returnDate": returnDate, "children": children, 
        "infants": infants, "travelClass": travelClass, "includedAirlineCodes": includedAirlineCodes, 
        "excludedAirlineCodes": excludedAirlineCodes, "nonStop": nonStop, "currencyCode": currencyCode, 
        "maxPrice": maxPrice, "max": max}


def request_flight_offers(search_dict, token_tuple):
    """
    Fonction qui permet d'effectuer la requête "flight offers" sur l'API Amadeus et de récupérer le contenu sous format JSON
    Paramètres :
        search_dict : le dictionnaire contenant les paramètres de la requête
        token : le token renvoyé par la fonction get_token
    Return:
        le json de la requête
    """
    if is_token_expired(token_tuple):
        token_tuple = get_token(token_tuple[3], token_tuple[4])
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode="+search_dict["originLocationCode"]+"&destinationLocationCode="+search_dict["destinationLocationCode"]+"&departureDate="+search_dict["departureDate"]+"&adults="+search_dict["adults"]
    if search_dict["returnDate"] != "":
        url += "&returnDate="+search_dict["returnDate"]
    if search_dict["children"] != "":
        url += "&children="+search_dict["children"]
    if search_dict["infants"] != "":
        url += "&infants="+search_dict["infants"]
    if search_dict["travelClass"] != "":
        url += "&travelClass="+search_dict["travelClass"]
    if search_dict["includedAirlineCodes"] != "":
        url += "&includedAirlineCodes="+search_dict["includedAirlineCodes"]
    if search_dict["excludedAirlineCodes"] != "":
        url += "&excludedAirlineCodes="+search_dict["excludedAirlineCodes"]
    if search_dict["nonStop"] != "":
        url += "&nonStop="+search_dict["nonStop"]  
    if search_dict["currencyCode"] != "":
        url += "&currencyCode="+search_dict["currencyCode"] 
    if search_dict["maxPrice"] != "":
        url += "&maxPrice="+search_dict["maxPrice"] 
    if search_dict["max"] != "":
        url += "&max="+search_dict["max"]
    response = requests.get(url, headers = {"authorization": "Bearer "+token_tuple[0]})
    response_json = json.loads(response.content)
    return response_json  


def export_json(json_file, file_name, file_path = ""):
    """
    Fonction qui réalise l'export des fichiers json des requêtes
    Paramètres :
        json_file : le fichier json à exporter
        file_name : le nom du fichier à exporter
        file_path : le chemin vers lequel envoyer le fichier, par défaut dans le dossier contenant le code du projet
    """
    with open(file_path+file_name, "w") as f:
        json.dump(json_file, f)

def mongodb_connection(mongo_atlas_username, mongo_atlas_password, mongo_cluster_adress):
    """
    Fonction qui crée la connection au serveur mongo_atlas
    Paramètres :
        mongo_atlas_username : le username du projet mongo atlas
        mongo_atlas_password : le password du projet mongo atlas
        mongo_cluster_adress : l'adresse du cluster mongo atlas
    Return:
        le client
    """
    conn_str = "mongodb+srv://"+mongo_atlas_username+":"+mongo_atlas_password+"@"+mongo_cluster_adress+"/test?retryWrites=true&w=majority"
    client = MongoClient(conn_str, serverSelectionTimeoutMS=5000)
    try:
        print(client.server_info())
    except Exception:
        print("Unable to connect to the server.")
    return client

def mongodb_search_iata(city_to_be_find : str, mongodb_collection, country : str = ""):
    """
    Fonction qui effectue une requête mongodb sur les villes et renvoie les codes iata correspondant
    Paramètres :
        mongodb_collection : le nom de la collection mongo dans laquelle effectuer la recherche
        city_to_be_find : la ville à rechercher dans la base de données
        country : le pays dans lequel est situé la ville si on souhaite le préciser (optionnel)
    Return:
        le résultat de la requête mongodb
    """
    city_regex = re.compile(r"\b"+city_to_be_find+", .*"+country)
    collection = mongodb_collection
    return collection.find(filter = {"airport_location" : city_regex})


def get_iata(locations_list, mongodb_collection):
    """
    Fonction qui effectue les requêtes mongodb à partir d'une liste de villes et renvoie 
    une liste des codes IATA des aéroports présents dans ces villes
    Paramètres :
        locations_list : une liste de listes de dimensions max 2 avec : [nom_ville, nom_pays(optionnel)]
        mongodb_collection : le nom de la collection mongo dans laquelle effectuer la recherche
    Return:
        la liste des iata obtenue dans la base de données
    """
    airport_iata_list = []

    for city in locations_list:
        try:
            airport_list_in_city = list(mongodb_search_iata(city[0], mongodb_collection, city[1]))
        except:
            airport_list_in_city = list(mongodb_search_iata(city[0], mongodb_collection))
        for airport in airport_list_in_city:
            airport_iata_list.append(airport['IATA'])

    return airport_iata_list

def get_iata_one_city(location, mongodb_collection):
    """
    Fonction qui effectue les requêtes mongodb à partir d'une ville et renvoie 
    une liste des codes IATA des aéroports présents dans ces villes
    Paramètres :
        locations_list : une liste de listes de dimensions max 2 avec : [nom_ville, nom_pays(optionnel)]
        mongodb_collection : le nom de la collection mongo dans laquelle effectuer la recherche
    Return:
        la liste des iata obtenue dans la base de données
    """
    airport_iata_list = []

    airport_list_in_city = list(mongodb_search_iata(location, mongodb_collection))
    for airport in airport_list_in_city:
        airport_iata_list.append(airport['IATA'])

    return airport_iata_list