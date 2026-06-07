# -*- coding: utf-8 -*-
"""
step1_build_matrix_osm.py — MODE OSM (reseau routier reel) : construit la matrice
des TEMPS de trajet sur le vrai graphe OpenStreetMap, sur les MEMES 43 points.

ADDITIF : ne touche ni a step1_build_matrix.py, ni a travel_time_matrix.csv,
ni a results.csv. Produit uniquement des fichiers suffixes _osm.

Entree  : coords.csv (lon,lat des 43 points ; le point n0 est le depot).
Sorties :
    road_graph.graphml              le reseau routier mis en cache (reproductibilite)
    travel_time_matrix_osm.csv      matrice n x n ASYMETRIQUE (secondes ; sens uniques)
    travel_time_matrix_osm_sym.csv  matrice SYMETRISEE (T + T^T)/2, pour 2-opt
    snapping_osm.csv                erreur de rattachement point -> noeud (metres)
    osm_build_stats.json            stats d'execution (pour le rapport, sans rien inventer)

Necessite Internet (telechargement OSMnx) + scikit-learn (nearest_nodes sous Windows).
Si OSMnx echoue, le script s'arrete avec une erreur explicite (aucun resultat fabrique).
"""
import csv
import json
import math
import time
import os

# --- parametres OSM (memes choix documentes que le mode hypothese de step1) ---
COORDS_FILE = "coords.csv"
BUFFER_M = 600                 # marge (m) autour des points pour capter le reseau
HWY_SPEEDS = {                 # vitesses (km/h) par type de voie -- a justifier
    "residential": 30, "living_street": 20, "tertiary": 40,
    "secondary": 50, "primary": 60, "trunk": 70,
}
FALLBACK_SPEED = 30
GRAPHML_FILE = "road_graph.graphml"


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_coords(path=COORDS_FILE):
    coords = []
    with open(path, newline="") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            coords.append((float(row[0]), float(row[1])))   # (lon, lat)
    return coords


def write_matrix(path, M):
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows([[f"{x:.4f}" for x in row] for row in M])


def main():
    import osmnx as ox
    import networkx as nx

    coords = load_coords()
    n = len(coords)
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    clat, clon = sum(lats) / n, sum(lons) / n
    radius = max(haversine_m(clat, clon, la, lo) for la, lo in zip(lats, lons))
    dist = radius + BUFFER_M
    print(f"{n} points charges. Centroide ({clat:.5f}, {clon:.5f}).")
    print(f"Telechargement du reseau 'drive' (rayon {dist:.0f} m)...")

    t0 = time.time()
    G = ox.graph_from_point((clat, clon), dist=dist, network_type="drive")
    n_nodes_raw = G.number_of_nodes()

    # composante fortement connexe maximale : garantit que TOUTES les paires sont
    # routables dans les deux sens (sinon Dijkstra renverrait des distances infinies).
    G = ox.truncate.largest_component(G, strongly=True)
    n_removed = n_nodes_raw - G.number_of_nodes()

    G = ox.routing.add_edge_speeds(G, hwy_speeds=HWY_SPEEDS, fallback=FALLBACK_SPEED)
    G = ox.routing.add_edge_travel_times(G)
    dl_time = time.time() - t0
    print(f"Reseau : {G.number_of_nodes()} noeuds, {G.number_of_edges()} aretes "
          f"({n_removed} noeuds hors composante connexe retires) en {dl_time:.1f} s.")

    ox.save_graphml(G, GRAPHML_FILE)
    print(f"Reseau sauvegarde -> {GRAPHML_FILE}")

    # --- rattachement (snapping) des 43 points aux noeuds du reseau ---
    nodes, snap = ox.distance.nearest_nodes(G, X=lons, Y=lats, return_dist=True)
    nodes = list(nodes)
    snap_max, snap_mean = max(snap), sum(snap) / n
    print(f"Snapping : distance point->route  max = {snap_max:.1f} m  "
          f"moyenne = {snap_mean:.1f} m.")
    with open("snapping_osm.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "lon", "lat", "node_id", "snap_dist_m"])
        for i in range(n):
            w.writerow([i, lons[i], lats[i], nodes[i], f"{snap[i]:.2f}"])

    # --- matrice ASYMETRIQUE des temps (Dijkstra sur travel_time) ---
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
    mean_tt = total / npairs if npairs else math.inf
    if unreachable:
        print(f"  /!\\ {unreachable} paires non connectees (ne devrait pas arriver "
              f"apres truncate strongly=True).")
    print(f"Temps moyen entre deux points (OSM, asym) : {mean_tt:.1f} s.")

    # --- matrice SYMETRISEE (T + T^T)/2 pour 2-opt ---
    S = [[(T[i][j] + T[j][i]) / 2.0 for j in range(n)] for i in range(n)]

    write_matrix("travel_time_matrix_osm.csv", T)
    write_matrix("travel_time_matrix_osm_sym.csv", S)
    print("Matrices ecrites : travel_time_matrix_osm.csv (asym), "
          "travel_time_matrix_osm_sym.csv (sym).")

    # --- asymetrie : a quel point les deux sens different (pour le rapport) ---
    asym_diffs = [abs(T[i][j] - T[j][i]) for i in range(n) for j in range(n) if i != j]
    asym_max = max(asym_diffs) if asym_diffs else 0.0
    asym_mean = sum(asym_diffs) / len(asym_diffs) if asym_diffs else 0.0

    stats = {
        "n_points": n, "radius_m": round(dist, 1),
        "nodes": G.number_of_nodes(), "edges": G.number_of_edges(),
        "nodes_removed_not_strongly_connected": n_removed,
        "download_seconds": round(dl_time, 1),
        "snap_max_m": round(snap_max, 2), "snap_mean_m": round(snap_mean, 2),
        "unreachable_pairs": unreachable,
        "mean_travel_time_s_asym": round(mean_tt, 2),
        "asym_diff_max_s": round(asym_max, 2), "asym_diff_mean_s": round(asym_mean, 2),
        "hwy_speeds_kmh": HWY_SPEEDS, "fallback_speed_kmh": FALLBACK_SPEED,
        "buffer_m": BUFFER_M,
    }
    with open("osm_build_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print("Stats ecrites -> osm_build_stats.json")
    print("-> lance maintenant : python step2_solve_osm.py")


if __name__ == "__main__":
    main()
