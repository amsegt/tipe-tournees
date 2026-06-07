# -*- coding: utf-8 -*-
"""
step5_calibrate_osm.py — MODE OSM : etalonnage des heuristiques contre l'optimum
exact (Held-Karp) sur les MEMES 7 sous-quartiers de 14 points qu'en hypothese.

ADDITIF. Reutilise :
  - step5_calibrate.pick_subquartier / ANCHORS / SUB_SIZE  -> sous-quartiers IDENTIQUES
  - tsp_core.py (algorithmes inchanges)
Difference avec step5 : la matrice de chaque sous-quartier est EXTRAITE de la
matrice OSM symetrisee complete (43x43), pas recalculee a vol d'oiseau.

Entree  : travel_time_matrix_osm_sym.csv, coords.csv
Sortie  : calibration_results_osm.csv  (meme format que calibration_results.csv)
"""
import csv
import statistics
import tsp_core as tsp
import step5_calibrate as base   # mêmes ancres, même selection des sous-quartiers

OSM_SYM = "travel_time_matrix_osm_sym.csv"


def fmt(sec):
    m, s = divmod(int(round(sec)), 60)
    return f"{m}min{s:02d}s"


def main():
    coords = base.load_coords()
    Dfull = tsp.read_matrix_csv(OSM_SYM)
    print(f"Matrice OSM symetrisee {len(Dfull)}x{len(Dfull)} chargee.")
    print(f"Etalonnage OSM sur {len(base.ANCHORS)} sous-quartiers de "
          f"{base.SUB_SIZE} points (memes ancres que le mode hypothese).\n")

    rows = []
    gaps_nn0, gaps_nnb, gaps_2opt = [], [], []

    header = (f"{'Sous-quartier':<16}{'Optimum (HK)':>14}{'PPV depot':>12}"
              f"{'PPV best':>11}{'2-opt':>10}")
    print(header); print("-" * len(header))

    for k, anchor in enumerate(base.ANCHORS, 1):
        idx = base.pick_subquartier(coords, anchor, base.SUB_SIZE)  # memes indices
        # sous-matrice EXTRAITE de la matrice OSM (depot = indice local 0)
        D = [[Dfull[a][b] for b in idx] for a in idx]

        nn0 = tsp.tour_length(tsp.nearest_neighbor(D, 0), D)
        nnb = tsp.tour_length(tsp.nearest_neighbor_best_start(D), D)
        _, opt = tsp.held_karp(D)
        two = tsp.tour_length(tsp.two_opt(tsp.nearest_neighbor_best_start(D), D), D)

        g0 = 100 * (nn0 - opt) / opt
        gb = 100 * (nnb - opt) / opt
        g2 = 100 * (two - opt) / opt
        gaps_nn0.append(g0); gaps_nnb.append(gb); gaps_2opt.append(g2)

        name = f"Q{k} (ancre {anchor})"
        print(f"{name:<16}{fmt(opt):>14}{'+'+format(g0,'.1f')+'%':>12}"
              f"{'+'+format(gb,'.1f')+'%':>11}{'+'+format(g2,'.1f')+'%':>10}")
        rows.append([name, base.SUB_SIZE, f"{opt:.2f}", f"{nn0:.2f}", f"{g0:.2f}",
                     f"{nnb:.2f}", f"{gb:.2f}", f"{two:.2f}", f"{g2:.2f}"])

    def stats(g):
        return statistics.mean(g), min(g), max(g)

    print("\n" + "=" * 60)
    print("DISTRIBUTION DES ECARTS A L'OPTIMUM EXACT — MODE OSM")
    print("=" * 60)
    print(f"{'Heuristique':<28}{'moyen':>9}{'min':>9}{'max':>9}")
    for label, g in [("Plus proche voisin (depot)", gaps_nn0),
                     ("Plus proche voisin (best)", gaps_nnb),
                     ("2-opt (sur meilleur PPV)", gaps_2opt)]:
        mo, mi, ma = stats(g)
        print(f"{label:<28}{'+'+format(mo,'.1f')+'%':>9}"
              f"{'+'+format(mi,'.1f')+'%':>9}{'+'+format(ma,'.1f')+'%':>9}")

    with open("calibration_results_osm.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sous_quartier", "n", "optimum_HK_s", "ppv_depot_s",
                    "ecart_ppv_depot_%", "ppv_best_s", "ecart_ppv_best_%",
                    "2opt_s", "ecart_2opt_%"])
        w.writerows(rows)
    n_exact = sum(1 for g in gaps_2opt if abs(g) < 1e-9)
    print(f"\n2-opt atteint l'optimum exact {n_exact}/{len(base.ANCHORS)} fois.")
    print("Fichier ecrit : calibration_results_osm.csv")


if __name__ == "__main__":
    main()
