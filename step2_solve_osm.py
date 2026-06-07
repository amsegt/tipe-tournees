# -*- coding: utf-8 -*-
"""
step2_solve_osm.py — MODE OSM : rejoue PPV / 2-opt sur la matrice OSM symetrisee.

ADDITIF : meme logique que step2_solve.py mais sur travel_time_matrix_osm_sym.csv.
Reutilise tsp_core.py TEL QUEL (algorithmes inchanges).

Entree  : travel_time_matrix_osm_sym.csv  (produit par step1_build_matrix_osm.py)
Sorties : results_osm.csv      (meme format que results.csv)
          best_tour_osm.json   (meme format que best_tour.json)

On reporte aussi, a titre informatif, le cout REEL ASYMETRIQUE du meilleur tour
(somme des temps reels dans le sens de parcours), lu dans la matrice asymetrique.
"""
import json
import csv
import time
import tsp_core as tsp

MATRIX_SYM = "travel_time_matrix_osm_sym.csv"
MATRIX_ASYM = "travel_time_matrix_osm.csv"


def fmt(sec):
    if sec == float("inf"):
        return "inf"
    m, s = divmod(int(round(sec)), 60)
    return f"{m}min{s:02d}s"


def asym_tour_length(order, A):
    """Cout reel d'un cycle dans le sens de parcours (matrice asymetrique)."""
    n = len(order)
    return sum(A[order[i]][order[(i + 1) % n]] for i in range(n))


def main():
    D = tsp.read_matrix_csv(MATRIX_SYM)          # deja symetrique (mode OSM)
    A = tsp.read_matrix_csv(MATRIX_ASYM)         # asymetrique (cout reel oriente)
    n = len(D)
    print(f"Matrice OSM symetrisee {n}x{n} chargee.")

    results = []   # (methode, longueur_sec, temps_calcul_s, tour)

    t0 = time.perf_counter()
    nn = tsp.nearest_neighbor(D, start=0)
    results.append(("Plus proche voisin (depart 0)", tsp.tour_length(nn, D),
                    time.perf_counter() - t0, nn))

    t0 = time.perf_counter()
    nnb = tsp.nearest_neighbor_best_start(D)
    results.append(("Plus proche voisin (meilleur depart)", tsp.tour_length(nnb, D),
                    time.perf_counter() - t0, nnb))

    t0 = time.perf_counter()
    opt = tsp.two_opt(nnb, D)
    results.append(("2-opt (sur meilleur PPV)", tsp.tour_length(opt, D),
                    time.perf_counter() - t0, opt))

    # Held-Karp saute (n=43 > 15), comme en mode hypothese.
    print(f"Held-Karp saute (n={n} > 15 : mur memoire).")

    print(f"\n{'Methode':<38}{'Temps cycle (sym)':>18}{'Calcul (s)':>13}")
    print("-" * 69)
    for name, length, ctime, _ in results:
        print(f"{name:<38}{fmt(length):>18}{ctime:>13.4f}")

    with open("results_osm.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["methode", "longueur_secondes", "temps_calcul_s", "tour"])
        for name, length, ctime, tour in results:
            w.writerow([name, f"{length:.2f}", f"{ctime:.4f}",
                        " ".join(map(str, tour))])

    best = min(results, key=lambda r: r[1])
    best_real = asym_tour_length(best[3], A)
    json.dump({"method": best[0], "length_seconds": best[1],
               "length_seconds_real_asym": round(best_real, 2), "order": best[3]},
              open("best_tour_osm.json", "w"), indent=2)
    print(f"\nMeilleur tour OSM : {best[0]}  ({fmt(best[1])} sym).")
    print(f"  Cout reel oriente (matrice asym) du meme ordre : {fmt(best_real)}.")
    print("Fichiers ecrits : results_osm.csv, best_tour_osm.json")
    print("-> lance : python step5_calibrate_osm.py  puis  python step3_plot_map_osm.py")


if __name__ == "__main__":
    main()
