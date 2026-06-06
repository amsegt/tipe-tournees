# -*- coding: utf-8 -*-
"""
make_report.py — Genere un RAPPORT PDF expliquant tout le projet :
    le probleme (TSP), les noeuds (donnees), chaque etape du pipeline,
    et chacun des algorithmes (plus proche voisin, 2-opt, Held-Karp, force brute),
    avec les resultats obtenus et les figures.

Aucune dependance lourde : uniquement matplotlib (deja installe).
Lit, si presents : results.csv, coords.csv, et les images PNG deja produites.

Sortie : rapport_tipe.pdf
"""
import os
import csv
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PAGE = (8.27, 11.69)          # A4 portrait (pouces)
INK = "#1A1A1A"
ACCENT = "#B85042"
TEAL = "#028090"
GREEN = "#2C5F2D"


# ==========================================================================
#  Petit moteur de mise en page : du texte qui "coule" sur plusieurs pages
# ==========================================================================
class Doc:
    def __init__(self, pdf):
        self.pdf = pdf
        self.fig = None
        self._new_page()

    def _new_page(self):
        if self.fig is not None:
            self._flush()
        self.fig = plt.figure(figsize=PAGE)
        self.y = 0.945
        self.fig.text(0.92, 0.035, "TIPE 13530 — Tournees de collecte",
                      ha="right", va="center", fontsize=7, color="#999999")

    def _flush(self):
        self.pdf.savefig(self.fig)
        plt.close(self.fig)
        self.fig = None

    def _need(self, h):
        if self.y - h < 0.06:
            self._new_page()

    def _line(self, text, x, size, lh, color=INK, family="sans-serif",
              weight="normal", style="normal"):
        self._need(lh)
        self.fig.text(x, self.y, text, fontsize=size, color=color,
                      family=family, weight=weight, style=style,
                      ha="left", va="top")
        self.y -= lh

    def h1(self, text):
        self.y -= 0.010
        self._need(0.060)
        self.fig.text(0.08, self.y, text, fontsize=17, color=INK,
                      weight="bold", ha="left", va="top")
        self.y -= 0.034
        self.fig.add_artist(plt.Line2D([0.08, 0.92], [self.y + 0.006, self.y + 0.006],
                                       color=ACCENT, lw=2,
                                       transform=self.fig.transFigure))
        self.y -= 0.018

    def h2(self, text):
        self.y -= 0.006
        self._line(text, 0.08, 12.5, 0.030, color=ACCENT, weight="bold")

    def body(self, text, width=92):
        for para in text.split("\n"):
            if not para.strip():
                self.y -= 0.010
                continue
            for ln in textwrap.wrap(para, width=width):
                self._line(ln, 0.08, 10, 0.0192)
        self.y -= 0.004

    def bullet(self, text, width=88):
        lines = textwrap.wrap(text, width=width)
        for k, ln in enumerate(lines):
            prefix = "•  " if k == 0 else "   "
            self._line(prefix + ln, 0.095, 10, 0.0192)

    def code(self, text, width=92):
        self.y -= 0.004
        for ln in text.split("\n"):
            for sub in textwrap.wrap(ln, width=width, subsequent_indent="    ",
                                     drop_whitespace=False) or [""]:
                self._line(sub.rstrip("\n"), 0.10, 8.3, 0.0165,
                           color="#173A5E", family="monospace")
        self.y -= 0.006

    def space(self, h=0.012):
        self.y -= h

    def finish(self):
        self._flush()


# ==========================================================================
#  Pages "image pleine"
# ==========================================================================
def image_page(pdf, path, title, caption):
    fig = plt.figure(figsize=PAGE)
    fig.text(0.08, 0.95, title, fontsize=15, weight="bold", color=INK,
             ha="left", va="top")
    fig.add_artist(plt.Line2D([0.08, 0.92], [0.925, 0.925], color=ACCENT, lw=2,
                              transform=fig.transFigure))
    if os.path.exists(path):
        img = plt.imread(path)
        ax = fig.add_axes([0.08, 0.16, 0.84, 0.74])
        ax.imshow(img)
        ax.axis("off")
    else:
        fig.text(0.5, 0.5, f"(image '{path}' absente — relance le script qui la produit)",
                 ha="center", va="center", fontsize=11, color="#999999")
    for k, ln in enumerate(textwrap.wrap(caption, width=100)):
        fig.text(0.08, 0.13 - k * 0.020, ln, fontsize=9.5, color="#444444",
                 ha="left", va="top")
    fig.text(0.92, 0.035, "TIPE 13530 — Tournees de collecte", ha="right",
             va="center", fontsize=7, color="#999999")
    pdf.savefig(fig)
    plt.close(fig)


# ==========================================================================
#  Donnees auxiliaires
# ==========================================================================
def read_results():
    rows = []
    if os.path.exists("results.csv"):
        with open("results.csv", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(row)
    return rows


def n_points():
    if os.path.exists("coords.csv"):
        return sum(1 for _ in open("coords.csv")) - 1
    return None


def fmt_sec(s):
    s = float(s)
    m, sec = divmod(int(round(s)), 60)
    return f"{m} min {sec:02d} s"


# ==========================================================================
#  Construction du rapport
# ==========================================================================
def cover(pdf, n):
    fig = plt.figure(figsize=PAGE)
    fig.add_artist(plt.Rectangle((0, 0.82), 1, 0.18, color=TEAL,
                                 transform=fig.transFigure))
    fig.text(0.5, 0.90, "TIPE — Tournees de collecte", ha="center", va="center",
             fontsize=23, weight="bold", color="white")
    fig.text(0.5, 0.855, "Du nuage de points au meilleur cycle : code & algorithmes",
             ha="center", va="center", fontsize=12, color="white")
    fig.text(0.5, 0.70, "Probleme du voyageur de commerce (TSP)\n"
                        "applique a une collecte de dechets a Meknès",
             ha="center", va="center", fontsize=14, color=INK)
    npts = f"{n} points" if n else "n points"
    fig.text(0.5, 0.58,
             f"Jeu de donnees : {npts} (1 depot + arrets)\n"
             "3 algorithmes compares : plus proche voisin, 2-opt, Held-Karp",
             ha="center", va="center", fontsize=11.5, color="#444444")
    fig.text(0.5, 0.40,
             "Pipeline :\n\n"
             "points.geojson  ->  step1  ->  matrice des temps\n"
             "matrice  ->  step2  ->  resolution & comparaison\n"
             "meilleur tour  ->  step3  ->  carte\n"
             "points  ->  step4  ->  graphe pondere + matrice d'adjacence",
             ha="center", va="center", fontsize=10.5, color=INK, family="monospace")
    fig.text(0.5, 0.10, "Rapport genere automatiquement par make_report.py",
             ha="center", va="center", fontsize=8.5, color="#999999",
             style="italic")
    pdf.savefig(fig)
    plt.close(fig)


def main():
    n = n_points()
    results = read_results()

    with PdfPages("rapport_tipe.pdf") as pdf:
        cover(pdf, n)
        d = Doc(pdf)

        # ---- 1. Le probleme et les noeuds ----
        d.h1("1. Le probleme et les noeuds")
        d.body(
            "On modelise une tournee de collecte par le PROBLEME DU VOYAGEUR DE "
            "COMMERCE (TSP, Travelling Salesman Problem). Un camion part d'un "
            "depot, doit passer une seule fois par chaque point de collecte, puis "
            "revenir au depot. On cherche le CYCLE de duree totale minimale.")
        d.h2("Les noeuds (sommets du graphe)")
        d.body(
            "Chaque point de collecte est un NOEUD. Les coordonnees viennent du "
            "fichier points.geojson (exporte de geojson.io), au format "
            "[longitude, latitude]. Regle essentielle : le PREMIER point du "
            "fichier est le DEPOT (depart et arrivee du cycle), il porte l'indice 0.")
        if n:
            d.body(f"Jeu de donnees courant : {n} noeuds (le depot n0 + {n-1} arrets). "
                   "Les coordonnees, dans l'ordre, sont stockees dans coords.csv.")
        d.h2("Les aretes (le graphe est complet)")
        d.body(
            "Entre deux noeuds quelconques on peut toujours se deplacer : le graphe "
            "est COMPLET. Le poids d'une arete est le TEMPS de trajet estime. Pour "
            f"{n or 'n'} noeuds il y a n(n-1)/2 = "
            f"{(n*(n-1)//2) if n else 'n(n-1)/2'} aretes non orientees : on ne peut "
            "pas toutes les dessiner lisiblement, mais la MATRICE D'ADJACENCE les "
            "contient toutes (voir derniere section, figures).")

        # ---- 2. Pipeline / les etapes ----
        d.h1("2. Les etapes du code (pipeline)")
        d.body("Le projet est decoupe en scripts independants, chacun produisant "
               "des fichiers lus par le suivant.")

        d.h2("step1_build_matrix.py — construire la matrice des temps")
        d.body(
            "Entree : points.geojson. Sortie : travel_time_matrix.csv (matrice n x n "
            "en SECONDES) et coords.csv. Deux methodes au choix (parametre METHOD) :")
        d.bullet('METHOD = "hypothesis" (defaut) : HYPOTHESE FORTE. Le temps entre '
                 'deux points = distance a vol d\'oiseau / vitesse moyenne constante. '
                 'Distance calculee par la formule de HAVERSINE (sur la sphere). '
                 'Aucun reseau, aucun acces Internet, instantane.')
        d.bullet('METHOD = "osm" : reseau routier reel via OSMnx. Le temps = plus '
                 'court chemin (Dijkstra) sur le vrai graphe des rues, ou chaque '
                 'troncon a une vitesse selon son type. Plus fidele, mais lourd '
                 '(Internet + dependances).')
        d.body("Formules clefs du mode hypothese :")
        d.code(
            "v_ms      = AVG_SPEED_KMH / 3.6          # km/h -> m/s\n"
            "d         = haversine_m(i, j) * DETOUR_FACTOR\n"
            "T[i][j]   = d / v_ms                      # temps = distance / vitesse")
        d.body("DETOUR_FACTOR = 1.0 correspond au vol d'oiseau pur (hypothese la plus "
               "forte) ; ~1.3 approche grossierement les detours routiers.")

        d.h2("step2_solve.py — resoudre et comparer")
        d.body(
            "Entree : travel_time_matrix.csv. Lance les trois algorithmes, mesure le "
            "temps de chaque cycle ET le temps de calcul, puis ecrit results.csv et "
            "best_tour.json. Si SYMMETRIZE = True, la matrice est rendue symetrique "
            "( T[i][j] <- (T[i][j]+T[j][i])/2 ) : necessaire pour que le 2-opt soit "
            "justifie. Held-Karp n'est lance que si n <= HELD_KARP_MAX (15 par "
            "defaut), car son cout explose.")

        d.h2("step3_plot_map.py — visualiser le meilleur tour")
        d.body(
            "Entree : best_tour.json + coords.csv (+ road_graph.graphml si dispo). "
            "Si le graphe routier existe (mode osm), trace l'itineraire reel le long "
            "des rues ; sinon trace un SCHEMA (segments droits dans l'ordre de "
            "visite). Sortie : best_tour.png.")

        d.h2("step4_graph.py — graphe pondere + matrice d'adjacence")
        d.body(
            "Entree : coords.csv. Construit le graphe (networkx), place chaque noeud "
            "a sa vraie position geographique et etiquette les aretes par leur "
            "distance. Sorties : graph_view.png (les K plus proches voisins, pour la "
            "lisibilite), adjacency_heatmap.png (toute la matrice n x n en carte de "
            "chaleur) et adjacency_matrix_m.csv (distances en metres).")

        d.h2("tsp_core.py — la bibliotheque d'algorithmes")
        d.body("Module importe par step2. Contient les trois algorithmes plus des "
               "utilitaires (lecture de matrice, symetrisation, longueur d'un tour, "
               "force brute de verification). Aucun acces reseau.")
        d.code(
            "def tour_length(tour, D):\n"
            "    n = len(tour)\n"
            "    return sum(D[tour[i]][tour[(i+1) % n]] for i in range(n))")

        # ---- 3. Algorithme 1 : plus proche voisin ----
        d.h1("3. Algorithme 1 — Plus proche voisin (glouton)")
        d.body(
            "Idee : partir d'un sommet, et a chaque etape aller vers le point NON "
            "ENCORE VISITE le plus proche. Simple et tres rapide, mais GLOUTON : il "
            "ne revient jamais sur ses choix et peut se piéger (les derniers sauts "
            "sont parfois tres longs).")
        d.h2("Pseudocode")
        d.code(
            "tour = [depart] ; visite[depart] = vrai ; courant = depart\n"
            "repeter (n-1) fois :\n"
            "    j* = argmin_{ j non visite } D[courant][j]\n"
            "    ajouter j* au tour ; visite[j*] = vrai ; courant = j*\n"
            "renvoyer tour")
        d.h2("Complexite et variante")
        d.bullet("Cout : O(n^2) pour un depart fixe.")
        d.bullet("nearest_neighbor_best_start : on relance depuis CHAQUE sommet et "
                 "on garde le meilleur tour -> O(n^3), souvent nettement meilleur.")
        d.body("Sans garantie d'optimalite : c'est une HEURISTIQUE (solution "
               "approchee, pas forcement la meilleure).")

        # ---- 4. Algorithme 2 : 2-opt ----
        d.h1("4. Algorithme 2 — 2-opt (amelioration locale)")
        d.body(
            "Idee : partir d'un tour existant (ici le meilleur plus-proche-voisin) "
            "et l'AMELIORER en defaisant les croisements. On choisit deux aretes du "
            "tour, on les retire, et on RENVERSE le segment intermediaire pour les "
            "reconnecter autrement. Si le nouveau tour est plus court, on le garde. "
            "On repete jusqu'a ne plus trouver d'amelioration (OPTIMUM LOCAL).")
        d.h2("Le test de gain")
        d.body("Pour les aretes (a,b) et (c,d) du tour, l'echange remplace a-b et "
               "c-d par a-c et b-d. Le gain est :")
        d.code(
            "delta = ( D[a][c] + D[b][d] ) - ( D[a][b] + D[c][d] )\n"
            "si delta < 0 :  on inverse le segment  tour[i..j]  (amelioration)")
        d.h2("Proprietes")
        d.bullet("Cout : O(n^2) par passe ; quelques passes suffisent en pratique.")
        d.bullet("SUPPOSE une matrice SYMETRIQUE (inverser un segment ne change pas "
                 "son cout) — d'ou le parametre SYMMETRIZE de step2.")
        d.bullet("Donne un OPTIMUM LOCAL : meilleur que le glouton, sans garantie "
                 "d'etre l'optimum global.")

        # ---- 5. Algorithme 3 : Held-Karp ----
        d.h1("5. Algorithme 3 — Held-Karp (exact)")
        d.body(
            "Resolution EXACTE par PROGRAMMATION DYNAMIQUE. On note C[(S, j)] le cout "
            "du plus court chemin qui part du depot 0, visite exactement l'ensemble "
            "de sommets S, et se termine au sommet j. On construit ces valeurs des "
            "petits ensembles vers les grands.")
        d.h2("Recurrence")
        d.code(
            "C[{j}, j]   = D[0][j]\n"
            "C[S, j]     = min_{ i in S, i != j }  ( C[S \\ {j}, i] + D[i][j] )\n"
            "cout optimal = min_j  ( C[{1..n-1}, j] + D[j][0] )")
        d.body("Les ensembles S sont codes par des ENTIERS (masques de bits) : le "
               "bit k vaut 1 si le sommet k est dans S. On reconstruit le tour en "
               "remontant les choix (le 'parent' memorise a chaque etape).")
        d.h2("Complexite — pourquoi on ne l'utilise que sur petites instances")
        d.bullet("Temps : O(n^2 * 2^n).  Memoire : O(n * 2^n).")
        d.bullet("Croissance EXPONENTIELLE : a n=43, 2^43 ~ 8.8 * 10^12 etats -> "
                 "impossible. D'ou HELD_KARP_MAX = 15 (au-dela on saute l'algo).")
        d.bullet("Usage : sur un sous-quartier de <= 15 points, il donne l'OPTIMUM "
                 "EXACT, qui sert d'ETALON pour mesurer l'ecart (%) des heuristiques.")
        d.h2("force brute (verification)")
        d.body("brute_force enumere les (n-1)! tours possibles : utilisable seulement "
               "pour n <= ~10. Sert a verifier que Held-Karp renvoie bien le meme "
               "optimum.")

        # ---- 6. Resultats ----
        d.h1("6. Resultats obtenus")
        if results:
            d.body("Comparaison sur le jeu de donnees courant "
                   f"({n} noeuds, mode hypothese, matrice symetrisee) :")
            d.space(0.004)
            # tableau
            d._need(0.05)
            d.fig.text(0.08, d.y, "Methode", fontsize=9.5, weight="bold", color=INK)
            d.fig.text(0.62, d.y, "Temps cycle", fontsize=9.5, weight="bold", color=INK)
            d.fig.text(0.80, d.y, "Calcul (s)", fontsize=9.5, weight="bold", color=INK)
            d.y -= 0.024
            best = min(results, key=lambda r: float(r["longueur_secondes"]))
            for row in results:
                is_best = row is best
                col = ACCENT if is_best else INK
                w = "bold" if is_best else "normal"
                d._need(0.022)
                name = row["methode"]
                d.fig.text(0.08, d.y, name[:46], fontsize=9, color=col, weight=w)
                d.fig.text(0.62, d.y, fmt_sec(row["longueur_secondes"]),
                           fontsize=9, color=col, weight=w)
                d.fig.text(0.80, d.y, f'{float(row["temps_calcul_s"]):.4f}',
                           fontsize=9, color=col, weight=w)
                d.y -= 0.022
            d.space(0.010)
            d.body(f"Meilleur cycle : {best['methode']} "
                   f"= {fmt_sec(best['longueur_secondes'])}. Le 2-opt ameliore "
                   "nettement le glouton : il supprime les croisements que le plus "
                   "proche voisin laisse en fin de parcours.")
            d.body("Note : Held-Karp est absent ci-dessus car n > 15. Pour obtenir "
                   "l'ecart exact a l'optimum, relancer le pipeline sur un "
                   "sous-quartier de <= 15 points (section 7 du README).")
        else:
            d.body("(results.csv introuvable — lance d'abord python step2_solve.py.)")

        # ---- 7. Parametres & rigueur ----
        d.h1("7. Parametres a defendre & limites du modele")
        d.bullet("AVG_SPEED_KMH : vitesse moyenne supposee (~20-30 km/h en ville) — "
                 "hypothese forte a justifier.")
        d.bullet("DETOUR_FACTOR : 1.0 (vol d'oiseau) a ~1.3 (approche les detours).")
        d.bullet("SYMMETRIZE : on moyenne les deux sens. Hypothese de modelisation "
                 "(les sens uniques rendent la vraie matrice asymetrique).")
        d.bullet("HELD_KARP_MAX : borne au-dela de laquelle l'exact est saute.")
        d.bullet("On resout un TSP ; la vraie collecte est un probleme de tournees "
                 "sur arcs (CARP/VRP) : simplification assumee.")
        d.bullet("Les temps sont des ESTIMATIONS (vitesses libres, sans trafic) : a "
                 "annoncer comme une premiere approximation / borne.")

        d.finish()

        # ---- Pages figures ----
        image_page(pdf, "graph_view.png",
                   "Figure 1 — Graphe pondere des points",
                   "Chaque noeud est place a sa vraie position (lon, lat). Les aretes "
                   "etiquetees relient chaque point a ses plus proches voisins ; les "
                   "etiquettes donnent la distance en metres. Le carre teal est le depot (0).")
        image_page(pdf, "adjacency_heatmap.png",
                   "Figure 2 — Matrice d'adjacence (graphe complet)",
                   "La matrice n x n des distances : sombre = proche, clair = lointain. "
                   "La diagonale nulle = distance d'un point a lui-meme. Les blocs sombres "
                   "revelent les groupes de points proches (structure du quartier).")
        image_page(pdf, "best_tour.png",
                   "Figure 3 — Meilleur cycle trouve",
                   "Le meilleur tour (ici 2-opt) dans l'ordre de visite. Les numeros "
                   "indiquent l'ordre de passage ; le carre est le depot, depart et arrivee "
                   "du cycle.")

    print("PDF ecrit -> rapport_tipe.pdf")


if __name__ == "__main__":
    main()
