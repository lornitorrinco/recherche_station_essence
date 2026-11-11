import json
import requests


def recuperer_json(coo , params , path , url="https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records" , api_key = None) :
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    x , y , rayon = coo
    trie_rayon = f"within_distance(geom , geom'POINT({x} {y})' , {rayon}km)"
    params["where"] = trie_rayon

    response = requests.get(url = url , params = params , headers = headers , timeout = 10)
    response.raise_for_status()

    print("Code HTTP :", response.status_code)
    print("Type MIME :", response.headers.get("Content-Type"))
    print("Aperçu de la réponse brute :")
    print(repr(response.text[:300]))

    data = response.json()

    with open(path , 'w' , encoding="utf-8") as f :
        json.dump(data , f, ensure_ascii=False, indent=2)

    print(f"Données enregistrées dans {path}")


def recuperer_coordonnee(url = "http://ip-api.com/json/"):
    response = requests.get(url , timeout= 5)
    response.raise_for_status()

    data = response.json()

    if data.get("status") == "fail":
        raise RuntimeError("Impossible de géolocaliser l'adresse IP")

    print(f"Coordonnée : {data["lat"]} , {data["lon"]}")
    return data["lat"], data["lon"]


def exploitation_stations(path):
    with open(path , 'r' , encoding="utf-8") as f :
        data = json.load(f)

    return data.get("results" , "Fichier invalide /!/ ")


def recherche_min(station_list : list , carburant : str):
    station_dispo = [station for station in station_list if (carburant in (station.get("carburants_disponibles") or []))]

    prix_srch = f"{carburant.lower()}_prix"
    liste_prix = [(station[prix_srch],station["id"]) for station in station_dispo]

    meilleur = min(liste_prix , key = lambda x : x[0])

    return meilleur


def recherche_max(station_list : list , carburant : str):
    station_dispo = [station for station in station_list if (carburant in (station.get("carburants_disponibles") or []))]

    prix_srch = f"{carburant.lower()}_prix"
    liste_prix = [(station[prix_srch],station["id"]) for station in station_dispo]

    pire = max(liste_prix , key = lambda x : x[0])

    return pire


def recherche_station(liste_station , id):
    bonne_station = None
    for station in liste_station :
        if station["id"] == id :
            bonne_station = station
    if bonne_station == None:
        print("Pas de station valide")
    else :
        print(f"Adresse : {bonne_station.get("adresse" , "adresse introuvable")} , à {bonne_station.get("ville" , "Ville introuvable")}")


if __name__ == "__main__" :
    lat , lon = (43.6045, 1.4440)
    rayon = int(input("Rayon max de recherche : "))
    recuperer_json(
        [lon, lat, rayon],
        params={"limit": 100,
                "refine": 'region:"Occitanie"'},
        path="extrait_carburants.json",
    )

    liste_station = exploitation_stations("extrait_carburants.json")
    min_prix = recherche_min(liste_station , "Gazole")
    recherche_station(liste_station , min_prix[1])
    print(min_prix[0])
    max_prix = recherche_max(liste_station , "Gazole")
    recherche_station(liste_station , max_prix[1])
    print(max_prix[0])

