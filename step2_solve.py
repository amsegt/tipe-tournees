# -*- coding: utf-8 -*-
"""
step2_solve.py — Lance les trois algorithmes sur la matrice des temps.

Entree  : travel_time_matrix.csv   (produit par step1)
Sorties : results.csv              (tableau comparatif)
          best_tour.json           (le meilleur tour, pour la visualisation)

N'utilise AUCUN acces reseau. S'appuie sur tsp_core.py.
"""
import json
import csv
import time
import tsp_core as tsp

# ====== PARAMETRES ========================================================
MATRIX_FILE = "travel_time_matrix.csv"
SYMMETRIZE = True        # True : matrice rendue symetrique (sens uniques moyennes)
HELD_KARP_MAX = 15       # au-dela, Held-Karp est trop lourd : on le saute
# ==========================================================================


def fmt(sec):
    """Secondes -> 'mm:ss' lisible."""
    if sec == float("inf"):
        return "inf"
    m, s = divmod(int(round(sec)), 60)
    return f"{m}min{s:02d}s"


def main():
    D = tsp.read_matrix_csv(MATRIX_FILE)
    n = len(D)
    print(f"Matrice {n}x{n} chargee.")
    if SYMMETRIZE:
        D = tsp.symmetrize(D)
        print("Matrice symetrisee (hypothese de modelisation a defendre).")

    results = []   # (methode, longueur_sec, temps_calcul_s, tour)

    # --- Plus proche voisin (depuis le sommet 0) ---
    t0 = time.perf_counter()
    nn = tsp.nearest_neighbor(D, start=0)
    results.append(("Plus proche voisin (depart 0)", tsp.tour_length(nn, D),
                    time.perf_counter() - t0, nn))

    # --- Plus proche voisin (meilleur depart) ---
    t0 = time.perf_counter()
    nnb = tsp.nearest_neighbor_best_start(D)
    results.append(("Plus proche voisin (meilleur depart)", tsp.tour_length(nnb, D),
                    time.perf_counter() - t0, nnb))

    # --- 2-opt (applique au meilleur PPV) ---
    t0 = time.perf_counter()
    opt = tsp.two_opt(nnb, D)
    results.append(("2-opt (sur meilleur PPV)", tsp.tour_length(opt, D),
                    time.perf_counter() - t0, opt))

    # --- Held-Karp (exact) si l'instance est assez petite ---
    if n <= HELD_KARP_MAX:
        t0 = time.perf_counter()
        hk, hk_cost = tsp.held_karp(D)
        results.append(("Held-Karp (exact)", hk_cost,
                        time.perf_counter() - t0, hk))
    else:
        print(f"Held-Karp saute (n={n} > {HELD_KARP_MAX} : mur memoire).")
        print("  -> pour l'etalonner, relance sur un sous-graphe de <= 15 points.")

    # --- Affichage ---
    print(f"\n{'Methode':<38}{'Temps cycle':>12}{'Calcul (s)':>13}")
    print("-" * 63)
    for name, length, ctime, _ in results:
        print(f"{name:<38}{fmt(length):>12}{ctime:>13.4f}")

    # --- Ecarts a la reference (si Held-Karp dispo) ---
    opt_ref = next((L for nme, L, _, _ in results if "Held-Karp" in nme), None)
    if opt_ref:
        print(f"\nEcart a l'optimum exact ({fmt(opt_ref)}) :")
        for name, length, _, _ in results:
            if "Held-Karp" not in name and opt_ref > 0:
                print(f"  {name:<38}+{100*(length-opt_ref)/opt_ref:5.2f} %")

    # --- Sauvegardes ---
    with open("results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["methode", "longueur_secondes", "temps_calcul_s", "tour"])
        for name, length, ctime, tour in results:
            w.writerow([name, f"{length:.2f}", f"{ctime:.4f}",
                        " ".join(map(str, tour))])

    best = min(results, key=lambda r: r[1])
    json.dump({"method": best[0], "length_seconds": best[1], "order": best[3]},
              open("best_tour.json", "w"), indent=2)
    print(f"\nMeilleur tour : {best[0]}  ({fmt(best[1])}).")
    print("Fichiers ecrits : results.csv, best_tour.json")
    print("-> visualise avec :  python step3_plot_map.py")


if __name__ == "__main__":
    main()
