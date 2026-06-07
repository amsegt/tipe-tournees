# -*- coding: utf-8 -*-
"""
step3_plot_map_osm.py — MODE OSM : trace le meilleur cycle 2-opt sur le VRAI
fond de carte routier (rues), pas un schema. Objectif 4 de la MCOT.

ADDITIF. Entrees : road_graph.graphml, best_tour_osm.json, coords.csv
Sorties : best_tour_osm.png   (carte rues, haute resolution)
          best_tour_osm.html  (carte interactive folium, si disponible)
"""
import json
import csv
import matplotlib
matplotlib.use("Agg")
import osmnx as ox


def load_coords(path="coords.csv"):
    coords = []
    with open(path, newline="") as f:
        r = csv.reader(f); next(r)
        for row in r:
            coords.append((float(row[0]), float(row[1])))
    return coords


def build_routes(G, order, stop_nodes):
    routes, seq = [], order + [order[0]]
    for a, b in zip(seq[:-1], seq[1:]):
        routes.append(ox.routing.shortest_path(G, stop_nodes[a], stop_nodes[b],
                                               weight="travel_time"))
    return routes


def plot_png(G, order, coords, stop_nodes):
    import matplotlib.pyplot as plt
    routes = build_routes(G, order, stop_nodes)
    lons = [c[0] for c in coords]; lats = [c[1] for c in coords]
    fig, ax = ox.plot_graph_routes(
        G, routes, route_colors="#B85042", route_linewidth=3,
        node_size=0, bgcolor="white", edge_color="#DDDDDD",
        edge_linewidth=0.6, show=False, close=False)
    ax.scatter(lons, lats, c="#2C5F2D", s=55, zorder=5, edgecolors="white")
    ax.scatter([lons[order[0]]], [lats[order[0]]], c="#028090", s=150, zorder=6,
               edgecolors="white", marker="s", label="depart/depot")
    ax.set_title("Meilleur cycle 2-opt sur le reseau routier reel (OSM) — Meknes")
    ax.legend(loc="upper right")
    fig.savefig("best_tour_osm.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("Carte rues OSM -> best_tour_osm.png")


def plot_folium(G, order, coords, stop_nodes):
    try:
        import folium
    except ImportError:
        print("(folium absent : HTML interactif saute)")
        return
    routes = build_routes(G, order, stop_nodes)
    clat = sum(c[1] for c in coords) / len(coords)
    clon = sum(c[0] for c in coords) / len(coords)
    m = folium.Map(location=[clat, clon], zoom_start=15, tiles="OpenStreetMap")
    for route in routes:
        pts = [(G.nodes[nd]["y"], G.nodes[nd]["x"]) for nd in route]
        folium.PolyLine(pts, color="#B85042", weight=4, opacity=0.85).add_to(m)
    for k, i in enumerate(order):
        lon, lat = coords[i]
        folium.CircleMarker([lat, lon], radius=5, color="#2C5F2D",
                            fill=True, fill_opacity=0.9,
                            popup=f"arret {k} (point {i})").add_to(m)
    lon0, lat0 = coords[order[0]]
    folium.Marker([lat0, lon0], popup="depot (depart/arrivee)",
                  icon=folium.Icon(color="cadetblue", icon="home")).add_to(m)
    m.save("best_tour_osm.html")
    print("Carte interactive -> best_tour_osm.html")


def main():
    order = json.load(open("best_tour_osm.json"))["order"]
    coords = load_coords()
    G = ox.load_graphml("road_graph.graphml")
    for _, _, data in G.edges(data=True):           # graphml stocke en texte
        for key in ("travel_time", "length", "speed_kph"):
            if key in data:
                try:
                    data[key] = float(data[key])
                except (TypeError, ValueError):
                    pass
    lons = [c[0] for c in coords]; lats = [c[1] for c in coords]
    stop_nodes = list(ox.distance.nearest_nodes(G, X=lons, Y=lats))
    plot_png(G, order, coords, stop_nodes)
    plot_folium(G, order, coords, stop_nodes)


if __name__ == "__main__":
    main()
