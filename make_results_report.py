# -*- coding: utf-8 -*-
"""
make_results_report.py — RAPPORT PDF des RESULTATS (point b, version PDF).

Reprend, commente et presente tous les resultats des algorithmes :
  - la comparaison sur l'instance reelle (43 points)  -> results.csv
  - l'etalonnage contre l'optimum exact (Held-Karp)   -> calibration_results.csv
avec les figures produites. Reutilise le moteur de mise en page de make_report.py.

Sortie : resultats_tipe.pdf
"""
import os
import csv
import statistics
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from make_report import Doc, image_page, PAGE, INK, ACCENT, TEAL


def fmt(sec):
    sec = float(sec)
    m, s = divmod(int(round(sec)), 60)
    return f"{m} min {s:02d} s"


def read_results():
    rows = []
    with open("results.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def read_calibration():
    rows = []
    with open("calibration_results.csv", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def cover(pdf):
    fig = plt.figure(figsize=PAGE)
    fig.add_artist(plt.Rectangle((0, 0.80), 1, 0.20, color=TEAL,
                                 transform=fig.transFigure))
    fig.text(0.5, 0.90, "Resultats & comparaison des algorithmes",
             ha="center", va="center", fontsize=20, weight="bold", color="white")
    fig.text(0.5, 0.855, "TIPE 13530 — Optimisation des tournees de collecte (Meknes)",
             ha="center", va="center", fontsize=12, color="white")
    fig.text(0.5, 0.66,
             "Plus proche voisin  •  2-opt  •  Held-Karp\n\n"
             "1) comparaison sur l'instance reelle (43 points)\n"
             "2) etalonnage contre l'optimum exact sur sous-quartiers <= 15 points",
             ha="center", va="center", fontsize=12.5, color=INK)
    fig.text(0.5, 0.40,
             "Le 2-opt s'avere quasi-optimal : ecart moyen +0,9 %\n"
             "a l'optimum exact, contre +14,4 % pour le plus proche voisin.",
             ha="center", va="center", fontsize=12, color=ACCENT, weight="bold")
    fig.text(0.5, 0.07, "Genere par make_results_report.py",
             ha="center", va="center", fontsize=8.5, color="#999999", style="italic")
    pdf.savefig(fig); plt.close(fig)


def main():
    results = read_results()
    calib = read_calibration()
    best = min(results, key=lambda r: float(r["longueur_secondes"]))
    g0 = [float(r["ecart_ppv_depot_%"]) for r in calib]
    gb = [float(r["ecart_ppv_best_%"]) for r in calib]
    g2 = [float(r["ecart_2opt_%"]) for r in calib]

    with PdfPages("resultats_tipe.pdf") as pdf:
        cover(pdf)
        d = Doc(pdf)

        # ---- 1. Cadre ----
        d.h1("1. Cadre de l'experience")
        d.body(
            "On modelise la tournee de collecte par un TSP sur le graphe complet "
            "pondere G = (V, E, w) : V = les points de collecte, w(u, v) = le temps "
            "de trajet estime. On cherche le cycle hamiltonien de poids minimal "
            "(depart et retour au depot).")
        d.bullet("Instance reelle : 43 points (1 depot + 42 arrets) d'un quartier de Meknes.")
        d.bullet("Ponderation : mode hypothese — distance a vol d'oiseau (haversine) "
                 "parcourue a 30 km/h constants (DETOUR_FACTOR = 1.0). Hypothese forte, "
                 "assumee comme premiere approximation.")
        d.bullet("Matrice symetrisee : hypothese de graphe non oriente, requise pour 2-opt.")
        d.bullet("Held-Karp (exact) : non calculable a 43 points (mur memoire O(n.2^n)) ; "
                 "on l'emploie comme etalon sur des sous-quartiers <= 15 points.")

        # ---- 2. Resultats 43 points ----
        d.h1("2. Comparaison sur l'instance reelle (43 points)")
        d.space(0.004)
        d._need(0.05)
        d.fig.text(0.08, d.y, "Methode", fontsize=9.5, weight="bold", color=INK)
        d.fig.text(0.55, d.y, "Temps de cycle", fontsize=9.5, weight="bold", color=INK)
        d.fig.text(0.80, d.y, "Calcul (s)", fontsize=9.5, weight="bold", color=INK)
        d.y -= 0.026
        for row in results:
            is_best = row is best
            col = ACCENT if is_best else INK
            w = "bold" if is_best else "normal"
            d._need(0.024)
            d.fig.text(0.08, d.y, row["methode"][:44], fontsize=9, color=col, weight=w)
            d.fig.text(0.55, d.y, fmt(row["longueur_secondes"]), fontsize=9,
                       color=col, weight=w)
            d.fig.text(0.80, d.y, f'{float(row["temps_calcul_s"]):.4f}',
                       fontsize=9, color=col, weight=w)
            d.y -= 0.024
        d.space(0.012)
        d.h2("Lecture")
        d.bullet("Le PPV depuis le depot (18 min 12 s) illustre la myopie : longue "
                 "arete de retour subie. C'est la borne haute a battre.")
        d.bullet("Relancer le PPV depuis le meilleur sommet gagne ~10 % : le resultat "
                 "depend fortement du point de depart (parade O(n^3)).")
        d.bullet("Le 2-opt (13 min 23 s) gagne encore 18,6 % sur le meilleur PPV "
                 "(-26,5 % vs PPV-depot) en decroisant le tour : c'est le meilleur cycle.")
        d.bullet("Detail notable : le 2-opt (0,0007 s) calcule plus VITE que le "
                 "PPV-meilleur-depart (0,0029 s) tout en etant meilleur — une seule "
                 "recherche locale contre n constructions.")

        # ---- 3. Etalonnage ----
        d.h1("3. Etalonnage contre l'optimum exact (Held-Karp)")
        d.body("Held-Karp ne tournant pas a 43 points, on mesure la qualite reelle des "
               "heuristiques sur 7 sous-quartiers de 14 points, ou l'optimum exact est "
               "calculable. On obtient une distribution d'ecarts a l'optimum :")
        d.space(0.004)
        d._need(0.05)
        d.fig.text(0.08, d.y, "Heuristique", fontsize=9.5, weight="bold", color=INK)
        d.fig.text(0.50, d.y, "ecart moyen", fontsize=9.5, weight="bold", color=INK)
        d.fig.text(0.68, d.y, "min", fontsize=9.5, weight="bold", color=INK)
        d.fig.text(0.80, d.y, "max", fontsize=9.5, weight="bold", color=INK)
        d.y -= 0.026
        for label, g, hl in [("Plus proche voisin (depot)", g0, False),
                             ("Plus proche voisin (meilleur depart)", gb, False),
                             ("2-opt (sur meilleur PPV)", g2, True)]:
            col = ACCENT if hl else INK
            w = "bold" if hl else "normal"
            d._need(0.024)
            d.fig.text(0.08, d.y, label, fontsize=9, color=col, weight=w)
            d.fig.text(0.50, d.y, f"+{statistics.mean(g):.1f} %", fontsize=9, color=col, weight=w)
            d.fig.text(0.68, d.y, f"+{min(g):.1f} %", fontsize=9, color=col, weight=w)
            d.fig.text(0.80, d.y, f"+{max(g):.1f} %", fontsize=9, color=col, weight=w)
            d.y -= 0.024
        d.space(0.012)
        d.h2("Lecture")
        d.bullet("Le 2-opt est quasi-optimal : +0,9 % en moyenne, et il atteint "
                 "exactement l'optimum sur 2 des 7 sous-quartiers.")
        d.bullet("Le plus proche voisin peut deriver jusqu'a +24,8 % : une heuristique "
                 "de construction seule ne suffit pas.")
        d.bullet("Conclusion defendable : sur l'instance complete (43 points), ou "
                 "l'optimum est inconnu, le 2-opt fournit une solution dont on a "
                 "QUANTIFIE la qualite par extrapolation prudente.")

        # ---- 4. Limites ----
        d.h1("4. Lecture critique (rigueur de soutenance)")
        d.bullet("Les temps reposent sur l'hypothese forte (vol d'oiseau, vitesse "
                 "constante) : a annoncer comme borne / premiere approximation.")
        d.bullet("L'etalonnage donne un ecart sur petites instances ; l'extrapolation "
                 "a 43 points est plausible mais non demontree.")
        d.bullet("On resout un TSP ; la collecte reelle est un CARP — simplification "
                 "de modelisation explicite et assumee.")
        d.bullet("Prolongement : refaire la matrice en mode reseau routier reel (OSM) "
                 "et verifier si le classement des algorithmes reste le meme "
                 "(analyse de robustesse).")

        d.finish()

        # ---- figures ----
        if os.path.exists("calibration_gaps.png"):
            image_page(pdf, "calibration_gaps.png",
                       "Figure 1 — Ecart a l'optimum exact par sous-quartier",
                       "Pour chaque sous-quartier (<= 15 points), ecart en % a l'optimum "
                       "Held-Karp. Le 2-opt (rouge) reste colle a 0 % ; le plus proche "
                       "voisin (beige/orange) s'en eloigne nettement.")
        if os.path.exists("best_tour.png"):
            image_page(pdf, "best_tour.png",
                       "Figure 2 — Meilleur cycle (2-opt) sur les 43 points",
                       "Le cycle hamiltonien retenu, dans l'ordre de visite. Carre = depot.")
        if os.path.exists("graph_view.png"):
            image_page(pdf, "graph_view.png",
                       "Figure 3 — Graphe pondere des points",
                       "Les 43 points et leurs distances (plus proches voisins etiquetes).")
        if os.path.exists("adjacency_heatmap.png"):
            image_page(pdf, "adjacency_heatmap.png",
                       "Figure 4 — Matrice d'adjacence (graphe complet)",
                       "Matrice 43x43 des distances : sombre = proche, clair = lointain.")

    print("PDF ecrit -> resultats_tipe.pdf")


if __name__ == "__main__":
    main()
