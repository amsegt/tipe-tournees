# -*- coding: utf-8 -*-
"""
step3_plot_map.py — Visualise le meilleur tour trouve.

Entrees : best_tour.json, coords.csv, et si possible road_graph.graphml
Sortie  : best_tour.png

Deux modes :
  - si road_graph.graphml existe -> trace l'itineraire reel le long des rues ;
  - sinon -> trace un schema (points + segments dans l'ordre de visite).
Le mode "rues" lit un fichier local : aucun acces reseau necessaire.
"""
import json
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_coords(path="coords.csv"):
    coords = []
    with open(path, newline="") as f:
        r = csv.reader(f)
        next(r)                       # entete lon,lat
        for row in r:
            coords.append((float(row[0]), float(row[1])))   # (lon, lat)
    return coords


def plot_streets(order, coords):
    """Trace l'itineraire reel le long du reseau routier (graphml)."""
    import osmnx as ox
    G = ox.load_graphml("road_graph.graphml")
    # graphml stocke les attributs en texte : on reconvertit en nombres
    for _, _, data in G.edges(data=True):
        for key in ("travel_time", "length"):
            if key in data:
                try:
                    data[key] = float(data[key])
                except (TypeError, ValueError):
                    pass
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    stop_nodes = list(ox.distance.nearest_nodes(G, X=lons, Y=lats))

    routes = []
    seq = order + [order[0]]          # on referme le cycle
    for a, b in zip(seq[:-1], seq[1:]):
        routes.append(ox.routing.shortest_path(G, stop_nodes[a], stop_nodes[b],
                                                weight="travel_time"))
    fig, ax = ox.plot_graph_routes(
        G, routes, route_colors="#B85042", route_linewidth=3,
        node_size=0, bgcolor="white", edge_color="#DDDDDD",
        edge_linewidth=0.6, show=False, close=False)
    # marqueurs des arrets
    ax.scatter(lons, lats, c="#2C5F2D", s=60, zorder=5, edgecolors="white")
    ax.scatter([lons[order[0]]], [lats[order[0]]], c="#028090", s=140,
               zorder=6, edgecolors="white", marker="s", label="depart/depot")
    ax.legend(loc="upper right")
    fig.savefig("best_tour.png", dpi=200, bbox_inches="tight")
    print("Itineraire reel trace -> best_tour.png")


def plot_schema(order, coords):
    """Schema simple : points + ordre de visite (segments droits)."""
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    fig, ax = plt.subplots(figsize=(8, 8))
    seq = order + [order[0]]
    xs = [lons[i] for i in seq]
    ys = [lats[i] for i in seq]
    ax.plot(xs, ys, "-", color="#B85042", lw=1.8, zorder=2)
    ax.scatter(lons, lats, c="#2C5F2D", s=70, zorder=3, edgecolors="white")
    for k, i in enumerate(order):        # numero d'ordre de passage
        ax.annotate(str(k), (lons[i], lats[i]), fontsize=8, color="white",
                    ha="center", va="center", zorder=4)
    ax.scatter([lons[order[0]]], [lats[order[0]]], c="#028090", s=160,
               marker="s", zorder=3, edgecolors="white", label="depart/depot")
    ax.set_title("Ordre de visite (segments schematiques)")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.legend(); ax.set_aspect("equal", adjustable="datalim")
    fig.savefig("best_tour.png", dpi=200, bbox_inches="tight")
    print("Schema trace -> best_tour.png")


def main():
    order = json.load(open("best_tour.json"))["order"]
    coords = load_coords()
    if os.path.exists("road_graph.graphml"):
        try:
            plot_streets(order, coords)
            return
        except Exception as e:
            print(f"(mode rues indisponible : {e}) -> schema de secours.")
    plot_schema(order, coords)


if __name__ == "__main__":
    main()
