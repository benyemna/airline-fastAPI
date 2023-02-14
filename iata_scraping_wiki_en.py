from bs4 import BeautifulSoup as bs
import string
from urllib.request import urlopen
import re
from mongo_atlas_connection import *

# liste de l'alphabet pour requêter sur toutes les pages
alphabet = list(string.ascii_uppercase)

# boucle sur les pages par lettre, la structure des pages change à partir de la lettre S d'où 2 boucles différentes
for letter in alphabet[:17]:
    # écriture de l'url et chargement de la page puis chargement dans un élément soup
    try:
        url_airport_code = "https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_"
        page = urlopen(url_airport_code+letter)
    except:
        print("error :", letter)

    soup = bs(page, 'html.parser')

    # les codes iata ainsi que les infos à obtenir sont dans des éléments "td" d'une table
    liste_elt_td = soup.findAll("td")

    # retraitement des éléments pour ne récupérer que le texte
    liste_elt_td_text = []
    for elt in liste_elt_td:
        elt_text = elt.text.replace('\n', '').replace('[1]', '').replace('[2]', '').replace('[3]', '').replace('[4]', '').replace('[5]', '')
        liste_elt_td_text.append(elt_text)

    liste_elt_td_text = liste_elt_td_text[:len(liste_elt_td_text)-5]

    # extraction des informations qui nous intéressent sous forme de dictionnaire puis chargement dans la base de données
    index = 0

    while index < len(liste_elt_td_text)-5:
        iata_code = liste_elt_td_text[index]
        airport_name = liste_elt_td_text[index+2]
        airport_location = liste_elt_td_text[index+3]
        dictionnaire = {"IATA" : iata_code, "airport_name" : airport_name, "airport_location" : airport_location}
        iata_airportname_location_collection.insert_one(dictionnaire)
        index +=6

# boucle sur les pages par lettre, la structure des pages change à partir de la lettre S d'où 2 boucles différentes
# réalisation des mêmes étapes que précédemment
for letter in alphabet[18:]:
    try:
        url_airport_code = "https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_"
        page = urlopen(url_airport_code+letter)
    except:
        print("error :", letter)

    soup = bs(page, 'html.parser')

    liste_elt_td = soup.findAll("td")

    liste_elt_td_text = []
    for elt in liste_elt_td:
        elt_text = elt.text.replace('\n', '').replace('[1]', '')
        liste_elt_td_text.append(elt_text)

    liste_elt_td_text = liste_elt_td_text[:len(liste_elt_td_text)-5]

    index = 0

    while index < len(liste_elt_td_text)-3:
        iata_code = liste_elt_td_text[index]
        airport_name = liste_elt_td_text[index+2]
        airport_location = liste_elt_td_text[index+3]
        dictionnaire = {"IATA" : iata_code, "airport_name" : airport_name, "airport_location" : airport_location}
        iata_airportname_location_collection.insert_one(dictionnaire)
        index +=4
