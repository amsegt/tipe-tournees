# -*- coding: utf-8 -*-
"""
step4_graph.py — Represente tes points comme un GRAPHE PONDERE et l'affiche,
                 puis affiche / sauvegarde la MATRICE D'ADJACENCE.

Entree  : coords.csv            (lon,lat de chaque point, produit par step1)
          [points.geojson]      (utilise en secours si coords.csv absent)

Sorties : graph_view.png        le graphe : noeuds places a leur vraie position
                                geographique, aretes etiquetees par la DISTANCE.
          adjacency_heatmap.png la matrice d'adjacence (n x n) en carte de chaleur
                                -> c'est le graphe COMPLET pondere du TSP.
          adjacency_matrix_m.csv la matrice d'adjacence (distances, en METRES).

Le graphe d'un TSP est COMPLET (toute paire de points est reliee). Dessiner les
n(n-1)/2 aretes etiquetees serait illisible : pour la lecture on n'etiquette que
les K plus proches voisins de chaque noeud (parametre K). La matrice d'adjacence,
elle, contient TOUTES les aretes : c'est la representation complete et fidele.
"""
import os
import csv
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

# ====== PARAMETRES A AJUSTER ==============================================
COORDS_FILE = "coords.csv"
POINTS_FILE = "points.geojson"     # secours si coords.csv absent
K = 3                              # nb de plus proches voisins etiquetes (lisibilite)
SHOW_COMPLETE = False              # True : dessine aussi (en gris pale) toutes les aretes
LABEL_UNIT = "m"                   # "m" (metres) ou "km"
# ==========================================================================


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance a vol d'oiseau en metres entre deux points (lat/lon)."""
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_coords():
    """Renvoie la liste des (lon, lat). Le point n0 est le depot."""
    if os.path.exists(COORDS_FILE):
        coords = []
        with open(COORDS_FILE, newline="") as f:
            r = csv.reader(f)
            next(r)                                   # entete lon,lat
            for row in r:
                coords.append((float(row[0]), float(row[1])))
        return coords
    # secours : relire le GeoJSON
    data = json.load(open(POINTS_FILE, encoding="utf-8"))
    coords = []
    for feat in data.get("features", []):
        g = feat.get("geometry", {})
        if g.get("type") == "Point":
            coords.append((g["coordinates"][0], g["coordinates"][1]))
    return coords


def distance_matrix(coords):
    """Matrice n x n des distances a vol d'oiseau (METRES). Symetrique, diag = 0."""
    n = len(coords)
    D = np.zeros((n, n))
    for i in range(n):
        loni, lati = coords[i]
        for j in range(i + 1, n):
            d = haversine_m(lati, loni, coords[j][1], coords[j][0])
            D[i][j] = D[j][i] = d
    return D


def label_of(d_m):
    """Formate une distance pour l'etiquette d'arete."""
    if LABEL_UNIT == "km":
        return f"{d_m / 1000:.2f}"
    return f"{d_m:.0f}"


def build_graph(coords, D):
    """Construit le graphe networkx : noeuds positionnes, aretes = K plus proches."""
    n = len(coords)
    G = nx.Graph()
    for i, (lon, lat) in enumerate(coords):
        G.add_node(i, pos=(lon, lat))
    # aretes des K plus proches voisins (sans doublon grace au set de paires)
    seen = set()
    for i in range(n):
        order = sorted((j for j in range(n) if j != i), key=lambda j: D[i][j])
        for j in order[:K]:
            a, b = (i, j) if i < j else (j, i)
            if (a, b) not in seen:
                seen.add((a, b))
                G.add_edge(a, b, weight=D[a][b])
    return G


def plot_graph(coords, D, G):
    """Dessine le graphe pondere : noeuds geo-positionnes, aretes etiquetees."""
    pos = {i: (lon, lat) for i, (lon, lat) in enumerate(coords)}
    n = len(coords)
    fig, ax = plt.subplots(figsize=(11, 11))

    # (optionnel) toutes les aretes du graphe complet, en gris tres pale
    if SHOW_COMPLETE:
        for i in range(n):
            for j in range(i + 1, n):
                xi, yi = pos[i]; xj, yj = pos[j]
                ax.plot([xi, xj], [yi, yj], color="#000000", alpha=0.04,
                        lw=0.4, zorder=1)

    # aretes K-plus-proches : trait + etiquette de distance
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#B85042",
                           width=1.6, alpha=0.8)
    edge_labels = {(u, v): label_of(d["weight"]) for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                 font_size=6, font_color="#333333",
                                 bbox=dict(boxstyle="round,pad=0.1", fc="white",
                                           ec="none", alpha=0.6))

    # noeuds : depot (carre teal) + arrets (cercles verts)
    others = [i for i in range(n) if i != 0]
    nx.draw_networkx_nodes(G, pos, nodelist=others, ax=ax, node_size=180,
                           node_color="#2C5F2D", edgecolors="white")
    nx.draw_networkx_nodes(G, pos, nodelist=[0], ax=ax, node_size=320,
                           node_color="#028090", edgecolors="white",
                           node_shape="s")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7, font_color="white")

    unit = "km" if LABEL_UNIT == "km" else "m"
    ax.set_title(f"Graphe pondere des points (aretes = {K} plus proches voisins, "
                 f"distances en {unit})")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, ls=":", alpha=0.3)
    fig.savefig("graph_view.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Graphe pondere trace -> graph_view.png")


def plot_heatmap(D):
    """Affiche la matrice d'adjacence (distances) en carte de chaleur."""
    n = len(D)
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(D, cmap="viridis")
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("distance (m)")
    ax.set_title(f"Matrice d'adjacence {n}x{n} (graphe complet pondere)")
    ax.set_xlabel("point j"); ax.set_ylabel("point i")
    fig.savefig("adjacency_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Matrice d'adjacence (heatmap) -> adjacency_heatmap.png")


def save_and_preview_matrix(D):
    """Sauvegarde la matrice en CSV et en affiche un coin dans le terminal."""
    n = len(D)
    with open("adjacency_matrix_m.csv", "w", newline="") as f:
        csv.writer(f).writerows([[f"{x:.1f}" for x in row] for row in D])
    print("Matrice d'adjacence (metres) -> adjacency_matrix_m.csv")

    k = min(8, n)
    print(f"\nApercu de la matrice d'adjacence (coin {k}x{k}, distances en metres) :")
    head = "      " + "".join(f"{j:>8}" for j in range(k))
    print(head)
    for i in range(k):
        row = "".join(f"{D[i][j]:8.0f}" for j in range(k))
        print(f"{i:>4}  {row}")
    if n > k:
        print(f"  ... ({n}x{n} au total ; tout est dans adjacency_matrix_m.csv)")


def main():
    coords = load_coords()
    n = len(coords)
    print(f"{n} points charges (depot = point n0).")
    D = distance_matrix(coords)
    G = build_graph(coords, D)
    print(f"Graphe : {G.number_of_nodes()} noeuds, {G.number_of_edges()} aretes "
          f"dessinees (sur {n * (n - 1) // 2} possibles du graphe complet).")
    plot_graph(coords, D, G)
    plot_heatmap(D)
    save_and_preview_matrix(D)


if __name__ == "__main__":
    main()
