from dst_airlines_functions import mongodb_connection


# Mongo atlas client
mongo_atlas_username = "dstairlines_nov22"
mongo_atlas_password = "dl3Xd2Bo6Lx8zLqF"
mongo_cluster_adress = "clusterdstairlinesproje.cowapnq.mongodb.net"

client = mongodb_connection(mongo_atlas_username, mongo_atlas_password, mongo_cluster_adress)


# création ou instanciation de la base de données et des collections mongo_atlas
inspire_me_db = client["inspire_me_database"]
flight_offers_collection = inspire_me_db["flight_offers_collection"]
flight_offers_MRS_ATH_cron_collection = inspire_me_db["flight_offers_collection_MRS_ATH_cron"]
flight_offers_LYS_LIS_cron_collection = inspire_me_db["flight_offers_collection_LYS_LIS_cron"]
iata_collection = inspire_me_db["iata_collection"]
iata_airportname_location_collection  = inspire_me_db["iata_airportname_location_collection"]