from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from bson.json_util import dumps
from dst_airlines_functions import get_iata_one_city, get_token, create_search_dict_flight_offers, request_flight_offers
from mongo_atlas_connection import *

# definition API et sécurité
api = FastAPI(title="API DST Airlines", description = "API pour interraction avec la BDD DST Airlines", version = "1.0.0",
            openapi_tags=[{'name': 'user','description': "fonctions accessibles à tous les utilisateurs"}, 
                        {'name': 'admin','description': "fonctions accessibles uniquement à l'admin"}])

security = HTTPBasic()


# données statiques API
client_id_qmrt = "sBpJvjXswOMJsR4PPOsxdDU5v00o3ACA"
client_secret_qmrt = "sNpkAoobJ2NyUWDm"
token_tuple = get_token(client_id_qmrt, client_secret_qmrt)
authorized_users = {"user": "user", "": ""}
admin = {"admin": "admin"}
reponses = {
    200: {"description": "OK"},
    401: {"description": "non autorisé"},
    404: {"description": "ressource introuvable"},
    422: {"description": "erreur dans la requête"},
    500: {"description": "crash de l'application"}
}


# fonctions de vérif de droits d'accès
def verif_authentification(credentials: HTTPBasicCredentials = Depends(security)):
    """Fonction de vérification du mot de passe utilisateur
    """
    for user in list(authorized_users.keys()):
        current_username_bytes = credentials.username.encode("utf8")
        correct_username_bytes = user.encode("utf8")
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        if is_correct_username:
            current_password_bytes = credentials.password.encode("utf8")
            password = authorized_users[user]
            correct_password_bytes = password.encode("utf8")
            is_correct_password = secrets.compare_digest(
                current_password_bytes, correct_password_bytes
            )
            break
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    return True

def verif_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Fonction de vérification du mot de passe utilisateur
    """
    for user in list(admin.keys()):
        current_username_bytes = credentials.username.encode("utf8")
        correct_username_bytes = user.encode("utf8")
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        if is_correct_username:
            current_password_bytes = credentials.password.encode("utf8")
            password = admin[user]
            correct_password_bytes = password.encode("utf8")
            is_correct_password = secrets.compare_digest(
                current_password_bytes, correct_password_bytes
            )
            break
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin username or password"
        )
    return True


# définition des terminaisons de l'API
@api.get('/', name = "API fonctionnelle ?", tags=['user'])
def get_online():
    """Message API fonctionnelle
    """
    return {"detail": "API en fonctionnement"}


@api.get('/auth', name= "autentification user", responses = reponses, tags=["user"])
def get_auth(authorized: bool = Depends(verif_authentification)):
    if authorized:
        return {"detail": "authentification OK"}
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )


@api.get('/admin', name= "autentification admin", responses = reponses, tags=["admin"])
def get_auth(authorized: bool = Depends(verif_admin)):
    if authorized:
        return {"detail": "admin OK"}
    else:
        return {"detail": "non admin"}


@api.get('/route', name = "requête itinéraire", responses = reponses, tags=['user'])
def get_route(departure_city, arrival_city, date, authorized: bool = Depends(verif_authentification)):
    """Requête d'un itinéraire sur la base de données
    """

    if authorized:
        departure_airport_iata_list = get_iata_one_city(departure_city, iata_airportname_location_collection)
        arrival_airport_iata_list = get_iata_one_city(arrival_city, iata_airportname_location_collection)
        route_list = []
        for departure_airport in departure_airport_iata_list:
            for arrival_airport in arrival_airport_iata_list:
                if not departure_airport == arrival_airport:
                    response = list(flight_offers_collection.find(filter = {"route_info":{"departure_airport_iata": departure_airport, 
                                                                        "arrival_airport_iata": arrival_airport, 
                                                                        "route_date": date}}))
                    if not response == []:
                        route_list.append(response)
        route_list_json = dumps(route_list)
        return route_list_json

    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )


@api.post('/new_route', name = "Ajout itinéraire", responses = reponses, tags=["admin"])
def post_new_route(departure_city, arrival_city, date, authorized: bool = Depends(verif_admin)):
    """Ajout d'un itinéraire à la base de donnée
    """

    if authorized:
        
        departure_airport_iata_list = get_iata_one_city(departure_city, iata_airportname_location_collection)
        arrival_airport_iata_list = get_iata_one_city(arrival_city, iata_airportname_location_collection)
        for departure_airport in departure_airport_iata_list:
            for arrival_airport in arrival_airport_iata_list:
                if not departure_airport == arrival_airport:
                    response = list(flight_offers_collection.find(filter = {"route_info":{"departure_airport_iata": departure_airport, 
                                                                        "arrival_airport_iata": arrival_airport, 
                                                                        "route_date": date}}))
                    if response == []:
                        dict_request = create_search_dict_flight_offers(originLocationCode = departure_airport, destinationLocationCode = arrival_airport, departureDate = date)
                        dict_route = request_flight_offers(dict_request, token_tuple)
                        dict_route["route_info"] = {"departure_airport_iata" : departure_airport, "arrival_airport_iata" : arrival_airport, "route_date" : date}
                        flight_offers_collection.insert_one(dict_route)
        
        return {"detail": "new route added"}

    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin username or password"
        )


@api.delete('/delete_route', name = "Suppression itinéraire", responses = reponses, tags=["admin"])
def delete_route(departure_city, arrival_city, date, authorized: bool = Depends(verif_admin)):
    """Suppression d'un itinéraire de la base de donnée
    """

    if authorized:
        
        departure_airport_iata_list = get_iata_one_city(departure_city, iata_airportname_location_collection)
        arrival_airport_iata_list = get_iata_one_city(arrival_city, iata_airportname_location_collection)
        for departure_airport in departure_airport_iata_list:
            for arrival_airport in arrival_airport_iata_list:
                if not departure_airport == arrival_airport:
                    response = list(flight_offers_collection.find(filter = {"route_info":{"departure_airport_iata": departure_airport, 
                                                                        "arrival_airport_iata": arrival_airport, 
                                                                        "route_date": date}}))
                    if not response == []:
                        flight_offers_collection.delete_one({"route_info":{"departure_airport_iata": departure_airport, 
                                                                                    "arrival_airport_iata": arrival_airport, 
                                                                                    "route_date": date}})
        
        return {"detail": "route deleted"}

    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin username or password"
        )