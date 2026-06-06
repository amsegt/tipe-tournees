# -*- coding: utf-8 -*-
"""
step1_build_matrix.py — Construit la matrice des TEMPS de trajet entre tes points.

Deux methodes, au choix (parametre METHOD ci-dessous) :

  METHOD = "hypothesis"   (par defaut, AUCUNE dependance lourde, AUCUN reseau)
      HYPOTHESE FORTE : on remplace les trajets routiers reels par la distance
      a vol d'oiseau, parcourue a une VITESSE MOYENNE CONSTANTE.
      -> simplification grossiere (ignore le reseau, les sens uniques, les detours)
         mais immediate, reproductible, et utile comme premiere approximation
         ET comme point de comparaison avec la methode "osm".

  METHOD = "osm"          (reseau routier reel via OSMnx ; necessite Internet
                           + 'pip install osmnx scikit-learn')
      Temps = longueur du troncon / vitesse selon le type de voie, sur le vrai
      graphe routier OpenStreetMap. Plus fidele, plus lourd.

Entree  : points.geojson  (entites "Point", coordonnees [longitude, latitude])
Sorties : travel_time_matrix.csv  (matrice n x n, en SECONDES)
          coords.csv               (lon,lat de chaque point, dans l'ordre)
          road_graph.graphml       (UNIQUEMENT en mode "osm", pour la carte)
"""
import json
import csv
import math

# ====== PARAMETRES A AJUSTER ==============================================
POINTS_FILE = "points.geojson"
METHOD = "hypothesis"          # "hypothesis"  ou  "osm"

# --- parametres du mode "hypothesis" (hypothese forte) ---
AVG_SPEED_KMH = 30.0           # vitesse moyenne CONSTANTE supposee (km/h)
DETOUR_FACTOR = 1.0            # 1.0 = a vol d'oiseau pur (hypothese la plus forte)
                              # ~1.3 = relache un peu l'hypothese (approche les detours)

# --- parametres du mode "osm" ---
BUFFER_M = 600                 # marge (m) autour de tes points pour le reseau
HWY_SPEEDS = {                 # vitesses (km/h) par type de voie -- A JUSTIFIER
    "residential": 30, "living_street": 20, "tertiary": 40,
    "secondary": 50, "primary": 60, "trunk": 70,
}
FALLBACK_SPEED = 30
# ==========================================================================


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance a vol d'oiseau en metres entre deux points (lat/lon)."""
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_points(path):
    """Parse le GeoJSON : renvoie la liste des coordonnees (lon, lat) des Point.

    Le PREMIER point du fichier est considere comme le depot (depart/arrivee).
    """
    data = json.load(open(path, encoding="utf-8"))
    coords = []
    for feat in data.get("features", []):
        geom = feat.get("geometry", {})
        if geom.get("type") == "Point":
            lon, lat = geom["coordinates"][0], geom["coordinates"][1]
            coords.append((lon, lat))
    if len(coords) < 2:
        raise ValueError("Il faut au moins 2 points 'Point' dans le GeoJSON.")
    return coords


# --------------------------------------------------------------------------
# Methode 1 : HYPOTHESE FORTE (a vol d'oiseau, vitesse moyenne constante)
# --------------------------------------------------------------------------
def build_matrix_hypothesis(coords):
    """Matrice des temps (s) sous hypothese forte. Renvoie (T, temps_moyen)."""
    n = len(coords)
    v_ms = AVG_SPEED_KMH / 3.6                    # km/h -> m/s
    T = [[0.0] * n for _ in range(n)]
    total, npairs = 0.0, 0
    for i in range(n):
        loni, lati = coords[i]
        for j in range(n):
            if i != j:
                d = haversine_m(lati, loni, coords[j][1], coords[j][0]) * DETOUR_FACTOR
                T[i][j] = d / v_ms                # temps = distance / vitesse
                total += T[i][j]
                npairs += 1
    temps_moyen = total / npairs                  # temps moyen entre deux points
    return T, temps_moyen


# --------------------------------------------------------------------------
# Methode 2 : RESEAU ROUTIER REEL (OSMnx) -- importe seulement si demande
# --------------------------------------------------------------------------
def build_matrix_osm(coords):
    """Matrice des temps (s) sur le vrai reseau routier. Renvoie (T, temps_moyen)."""
    import osmnx as ox
    import networkx as nx
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    n = len(coords)

    clat, clon = sum(lats) / n, sum(lons) / n
    radius = max(haversine_m(clat, clon, la, lo) for la, lo in zip(lats, lons))
    dist = radius + BUFFER_M
    print(f"Telechargement du reseau routier (rayon {dist:.0f} m)...")
    G = ox.graph_from_point((clat, clon), dist=dist, network_type="drive")
    G = ox.routing.add_edge_speeds(G, hwy_speeds=HWY_SPEEDS, fallback=FALLBACK_SPEED)
    G = ox.routing.add_edge_travel_times(G)
    print(f"Reseau : {G.number_of_nodes()} noeuds, {G.number_of_edges()} aretes.")

    nodes, snap = ox.distance.nearest_nodes(G, X=lons, Y=lats, return_dist=True)
    nodes = list(nodes)
    print(f"Snapping : distance max point->route = {max(snap):.1f} m "
          f"(moyenne {sum(snap)/n:.1f} m).")

    T = [[0.0] * n for _ in range(n)]
    total, npairs, unreachable = 0.0, 0, 0
    for i in range(n):
        d = nx.single_source_dijkstra_path_length(G, nodes[i], weight="travel_time")
        for j in range(n):
            if i != j:
                if nodes[j] in d:
                    T[i][j] = d[nodes[j]]
                    total += T[i][j]; npairs += 1
                else:
                    T[i][j] = math.inf; unreachable += 1
    if unreachable:
        print(f"  /!\\ {unreachable} paires non connectees (reseau morcele).")
    ox.save_graphml(G, "road_graph.graphml")
    return T, (total / npairs if npairs else math.inf)


def fmt(sec):
    if sec == float("inf"):
        return "inf"
    m, s = divmod(int(round(sec)), 60)
    return f"{m}min{s:02d}s"


def main():
    coords = load_points(POINTS_FILE)
    n = len(coords)
    print(f"{n} points parses depuis {POINTS_FILE} (depot = point n°0).")

    if METHOD == "hypothesis":
        print(f"Methode : HYPOTHESE FORTE — vol d'oiseau x{DETOUR_FACTOR} a "
              f"{AVG_SPEED_KMH} km/h (constante).")
        T, temps_moyen = build_matrix_hypothesis(coords)
    elif METHOD == "osm":
        print("Methode : reseau routier reel (OSMnx).")
        T, temps_moyen = build_matrix_osm(coords)
    else:
        raise ValueError("METHOD doit valoir 'hypothesis' ou 'osm'.")

    # --- le temps moyen entre deux points ---
    print(f"\n>>> Temps moyen entre deux points : {temps_moyen:.1f} s "
          f"({fmt(temps_moyen)}).")

    # --- sauvegardes ---
    with open("travel_time_matrix.csv", "w", newline="") as f:
        csv.writer(f).writerows([[f"{x:.2f}" for x in row] for row in T])
    with open("coords.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lon", "lat"])
        w.writerows(coords)

    print("Fichiers ecrits : travel_time_matrix.csv, coords.csv"
          + (", road_graph.graphml" if METHOD == "osm" else ""))
    print("-> lance maintenant :  python step2_solve.py")


if __name__ == "__main__":
    main()
