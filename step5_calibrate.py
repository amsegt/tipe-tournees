# -*- coding: utf-8 -*-
"""
step5_calibrate.py — ETALONNAGE des heuristiques contre l'optimum exact.

But (cf. README sect.7 + annexe sect.5.7) : Held-Karp ne tourne pas sur 43 points.
Pour MESURER la qualite de PPV et 2-opt, on les compare a l'optimum EXACT sur
plusieurs SOUS-QUARTIERS de <= 15 points (ou Held-Karp est calculable), puis on
agrege les ecarts en une DISTRIBUTION.

Non destructif : lit coords.csv (les 43 points) mais n'ecrit AUCUN des fichiers
du pipeline principal. Sorties propres :
    calibration_results.csv   (un ecart par sous-quartier et par heuristique)
    calibration_gaps.png      (graphique des ecarts a l'optimum)

S'appuie sur tsp_core.py (memes algorithmes que step2) pour rester coherent.
"""
import csv
import math
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tsp_core as tsp

# ====== PARAMETRES (alignes sur step1 mode "hypothesis") ==================
COORDS_FILE = "coords.csv"
AVG_SPEED_KMH = 30.0          # meme vitesse constante que step1
DETOUR_FACTOR = 1.0           # meme hypothese (vol d'oiseau pur)
SUB_SIZE = 14                 # taille de chaque sous-quartier (<= 15 pour Held-Karp)
ANCHORS = [1, 8, 16, 24, 30, 38, 42]   # points d'ancrage (indices globaux) des sous-quartiers
# ==========================================================================


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
        next(r)                          # entete lon,lat
        for row in r:
            coords.append((float(row[0]), float(row[1])))   # (lon, lat)
    return coords


def submatrix(coords, idx):
    """Matrice des temps (s) du sous-quartier (mode hypothese, symetrique)."""
    v_ms = AVG_SPEED_KMH / 3.6
    m = len(idx)
    T = [[0.0] * m for _ in range(m)]
    for a in range(m):
        lona, lata = coords[idx[a]]
        for b in range(m):
            if a != b:
                lonb, latb = coords[idx[b]]
                d = haversine_m(lata, lona, latb, lonb) * DETOUR_FACTOR
                T[a][b] = d / v_ms
    return T


def pick_subquartier(coords, anchor, size):
    """Depot (0) + (size-1) points les plus proches de 'anchor' (depot exclu)."""
    lona, lata = coords[anchor]
    others = [i for i in range(len(coords)) if i != 0]
    others.sort(key=lambda i: haversine_m(lata, lona, coords[i][1], coords[i][0]))
    chosen = others[:size - 1]
    return [0] + chosen              # le depot reste l'indice local 0


def fmt(sec):
    m, s = divmod(int(round(sec)), 60)
    return f"{m}min{s:02d}s"


def main():
    coords = load_coords()
    print(f"{len(coords)} points charges depuis {COORDS_FILE}.")
    print(f"Etalonnage sur {len(ANCHORS)} sous-quartiers de {SUB_SIZE} points "
          f"(depot inclus), mode hypothese {AVG_SPEED_KMH} km/h.\n")

    rows = []                        # pour le CSV
    gaps_nn0, gaps_nnb, gaps_2opt = [], [], []

    header = (f"{'Sous-quartier':<16}{'Optimum (HK)':>14}{'PPV depot':>12}"
              f"{'PPV best':>11}{'2-opt':>10}")
    print(header)
    print("-" * len(header))

    for k, anchor in enumerate(ANCHORS, 1):
        idx = pick_subquartier(coords, anchor, SUB_SIZE)
        D = tsp.symmetrize(submatrix(coords, idx))

        nn0 = tsp.tour_length(tsp.nearest_neighbor(D, 0), D)
        nnb = tsp.tour_length(tsp.nearest_neighbor_best_start(D), D)
        opt_tour, opt = tsp.held_karp(D)
        two = tsp.tour_length(tsp.two_opt(tsp.nearest_neighbor_best_start(D), D), D)

        g0 = 100 * (nn0 - opt) / opt
        gb = 100 * (nnb - opt) / opt
        g2 = 100 * (two - opt) / opt
        gaps_nn0.append(g0); gaps_nnb.append(gb); gaps_2opt.append(g2)

        name = f"Q{k} (ancre {anchor})"
        print(f"{name:<16}{fmt(opt):>14}{'+'+format(g0,'.1f')+'%':>12}"
              f"{'+'+format(gb,'.1f')+'%':>11}{'+'+format(g2,'.1f')+'%':>10}")
        rows.append([name, SUB_SIZE, f"{opt:.2f}", f"{nn0:.2f}", f"{g0:.2f}",
                     f"{nnb:.2f}", f"{gb:.2f}", f"{two:.2f}", f"{g2:.2f}"])

    # --- synthese : la distribution des ecarts ---
    def stats(g):
        return (statistics.mean(g), min(g), max(g))

    print("\n" + "=" * 60)
    print("DISTRIBUTION DES ECARTS A L'OPTIMUM EXACT (sur tous les sous-quartiers)")
    print("=" * 60)
    print(f"{'Heuristique':<28}{'moyen':>9}{'min':>9}{'max':>9}")
    for label, g in [("Plus proche voisin (depot)", gaps_nn0),
                     ("Plus proche voisin (best)", gaps_nnb),
                     ("2-opt (sur meilleur PPV)", gaps_2opt)]:
        mo, mi, ma = stats(g)
        print(f"{label:<28}{'+'+format(mo,'.1f')+'%':>9}"
              f"{'+'+format(mi,'.1f')+'%':>9}{'+'+format(ma,'.1f')+'%':>9}")

    # --- CSV ---
    with open("calibration_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sous_quartier", "n", "optimum_HK_s", "ppv_depot_s",
                    "ecart_ppv_depot_%", "ppv_best_s", "ecart_ppv_best_%",
                    "2opt_s", "ecart_2opt_%"])
        w.writerows(rows)

    # --- figure : ecarts par sous-quartier ---
    labels = [f"Q{k}" for k in range(1, len(ANCHORS) + 1)]
    x = range(len(labels))
    width = 0.27
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - width for i in x], gaps_nn0, width, label="PPV (depot)",
           color="#C7B299")
    ax.bar(list(x), gaps_nnb, width, label="PPV (meilleur depart)",
           color="#E5A04C")
    ax.bar([i + width for i in x], gaps_2opt, width, label="2-opt",
           color="#B85042")
    ax.axhline(0, color="#2C5F2D", lw=1.4, label="optimum Held-Karp (0 %)")
    ax.set_ylabel("ecart a l'optimum exact (%)")
    ax.set_xlabel("sous-quartier (<= 15 points, Held-Karp calculable)")
    ax.set_title("Etalonnage des heuristiques contre l'optimum exact (Held-Karp)")
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis="y", ls=":", alpha=0.4)
    fig.savefig("calibration_gaps.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("\nFichiers ecrits : calibration_results.csv, calibration_gaps.png")


if __name__ == "__main__":
    main()
