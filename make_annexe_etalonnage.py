# -*- coding: utf-8 -*-
"""
make_annexe_etalonnage.py — ANNEXE TECHNIQUE dediee :
    "Etalonnage des heuristiques contre l'optimum exact (Held-Karp)".

Formalise le detail theorique (pourquoi etalonner, Held-Karp par programmation
dynamique, recurrence de Bellman, complexite) ET le detail des heuristiques
(PPV, PPV meilleur depart, 2-opt), la methodologie du script step5, la lecture
chiffree des resultats et les limites.

Lit calibration_results.csv pour rester exact. Formules via mathtext (pas de LaTeX).
Reutilise le moteur de mise en page de make_report.py.

Sortie : annexe_etalonnage_held_karp.pdf
"""
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from make_report import Doc, image_page, PAGE, INK, ACCENT, TEAL


# ---- helpers de redaction ------------------------------------------------
def formula(d, tex, size=14, height=0.05):
    d.space(0.006)
    d._need(height + 0.012)
    d.fig.text(0.5, d.y, tex, fontsize=size, color=INK, ha="center", va="top")
    d.y -= height
    d.space(0.008)


def rowN(d, cells, xs, header=False, bold=False, fs=8.4):
    d._need(0.025)
    color = TEAL if header else INK
    w = "bold" if (header or bold) else "normal"
    for c, x in zip(cells, xs):
        d.fig.text(x, d.y, c, fontsize=fs, color=color, weight=w)
    d.y -= 0.025


def insert_image(d, pdf, path, title, caption):
    if d.fig is not None:
        d._flush()
    image_page(pdf, path, title, caption)
    d._new_page()


def fmt(sec):
    sec = float(sec)
    m, s = divmod(int(round(sec)), 60)
    return f"{m} min {s:02d} s"


def cover(pdf):
    fig = plt.figure(figsize=PAGE)
    fig.add_artist(plt.Rectangle((0, 0.80), 1, 0.20, color=TEAL, transform=fig.transFigure))
    fig.text(0.5, 0.905, "Annexe technique", ha="center", va="center",
             fontsize=22, weight="bold", color="white")
    fig.text(0.5, 0.852, "Etalonnage des heuristiques\ncontre l'optimum exact (Held-Karp)",
             ha="center", va="center", fontsize=14, color="white")
    fig.text(0.5, 0.63,
             "Pourquoi et comment mesurer la qualite des heuristiques :\n"
             "detail theorique (programmation dynamique) et detail des\n"
             "heuristiques, methodologie, resultats chiffres et limites.",
             ha="center", va="center", fontsize=12.5, color=INK)
    fig.text(0.5, 0.45,
             "TIPE 13530 — Optimisation des tournees de collecte (Meknes)\n"
             "Brahim Amsegt — CPGE MP — session 2026",
             ha="center", va="center", fontsize=11.5, color="#444444")
    fig.text(0.5, 0.29,
             "Resultat cle : le 2-opt est quasi-optimal (+0,9 % en moyenne),\n"
             "contre +14,4 % pour le plus proche voisin.",
             ha="center", va="center", fontsize=11, color=ACCENT, style="italic")
    fig.text(0.5, 0.07, "Genere par make_annexe_etalonnage.py", ha="center", va="center",
             fontsize=8.5, color="#999999", style="italic")
    pdf.savefig(fig); plt.close(fig)


# ==========================================================================
def main():
    with open("calibration_results.csv", newline="") as f:
        calib = list(csv.DictReader(f))
    g0 = [float(r["ecart_ppv_depot_%"]) for r in calib]
    gb = [float(r["ecart_ppv_best_%"]) for r in calib]
    g2 = [float(r["ecart_2opt_%"]) for r in calib]

    with PdfPages("annexe_etalonnage_held_karp.pdf") as pdf:
        cover(pdf)
        d = Doc(pdf)

        # ---- A ----
        d.h1("A. Le probleme de fond : pourquoi etalonner ?")
        d.body("Sur l'instance reelle (43 points), une heuristique donne UN nombre — "
               "par exemple 2-opt = 13 min 23 s. Mais ce nombre, pris seul, ne dit rien "
               "sur sa qualite : est-ce le meilleur tour possible ? a 5 % de l'optimum ? "
               "a 40 % ? On ne peut pas le savoir, car l'optimum exact a 43 points est "
               "incalculable (TSP NP-difficile, mur memoire de Held-Karp a n ~ 20).")
        d.body("L'idee de l'etalonnage (annexe 5.7 : Held-Karp comme etalon sur des "
               "sous-graphes de 12 a 15 sommets) :")
        d.bullet("on REDUIT le probleme a des sous-quartiers <= 15 points, ou l'optimum "
                 "exact EST calculable ;")
        d.bullet("on y mesure de combien chaque heuristique S'ECARTE de l'optimum vrai ;")
        d.bullet("on en tire une DISTRIBUTION d'ecarts, extrapolee prudemment a "
                 "l'instance complete.")
        d.body("La grandeur mesuree est l'ecart relatif a l'optimum :")
        formula(d, r"$\mathrm{ecart} = 100 \times "
                   r"\frac{L_{\mathrm{heuristique}} - L_{\mathrm{optimum}}}"
                   r"{L_{\mathrm{optimum}}}\quad(\%)$", size=15, height=0.06)
        d.body("Un ecart de 0 % signifie que l'heuristique a trouve l'optimum exact.")

        # ---- B ----
        d.h1("B. L'etalon : Held-Karp en detail (la theorie)")
        d.body("Held-Karp est EXACT : il garantit l'optimum. Il y parvient non pas en "
               "enumerant les (n-1)!/2 tours (force brute), mais par PROGRAMMATION "
               "DYNAMIQUE, en reutilisant des calculs.")
        d.h2("L'etat")
        d.body("On fixe le depart au depot (sommet 0). Pour un sous-ensemble S de sommets "
               "contenant 0 et un sommet d'arrivee j dans S :")
        d.body("C(S, j) = cout du plus court chemin partant de 0, visitant exactement S, "
               "finissant en j.")
        d.h2("La recurrence de Bellman")
        d.body("Pour finir en j apres avoir visite S, on est forcement passe juste avant "
               "par un autre sommet i de S. On essaie tous les i et on garde le meilleur :")
        formula(d, r"$C(S, j) = \min_{i \in S \setminus \{j\}} "
                   r"\left[\, C(S \setminus \{j\},\, i) + w(i, j) \,\right]$",
                size=15, height=0.06)
        d.body("Cas de base (chemins directs depuis le depot) :")
        formula(d, r"$C(\{0, j\},\, j) = w(0, j)$", size=14, height=0.045)
        d.body("Cloture du cycle (une fois S = V, on revient au depot) : cout optimal =")
        formula(d, r"$\min_{j \neq 0} \left[\, C(V, j) + w(j, 0) \,\right]$",
                size=14, height=0.05)
        d.body("C'est exactement ce qu'implemente held_karp() : C[(1<<j, j)] = (D[0][j], 0) "
               "(base), la triple boucle size -> subset -> j (recurrence), puis "
               "min(... + D[j][0] ...) (cloture), suivie de la reconstruction du tour en "
               "remontant les predecesseurs memorises.")
        d.h2("Le bitmask")
        d.body("Le sous-ensemble S est code par un ENTIER en binaire : le bit k vaut 1 si "
               "le sommet k est dans S. D'ou 1<<j (le sommet j seul) et bits & ~(1<<j) "
               "(S prive de j). Cela rend la table compacte et rapide.")
        d.h2("Pourquoi c'est exact, et le mur de complexite")
        d.body("Programmation dynamique = on calcule chaque morceau de chemin une seule "
               "fois et on le reutilise (la force brute recalcule mille fois le bout "
               "A->B->C). Cout :")
        formula(d, r"$\mathrm{Temps}\ \ O(n^{2}\,2^{n}) \qquad "
                   r"\mathrm{Memoire}\ \ O(n\,2^{n})$", size=14, height=0.05)
        d.body("Il y a un etat par couple (sous-ensemble S, arrivee j), soit ~ n.2^n "
               "etats, chacun coutant un minimum sur ~ n predecesseurs. C'est "
               "EXPONENTIEL : impossible a 43 points, mais trivial a n=14 (2^14 = 16 384 "
               "sous-ensembles). D'ou le choix SUB_SIZE = 14 : assez grand pour etre "
               "representatif, assez petit pour que Held-Karp donne l'optimum en une "
               "fraction de seconde.")

        # ---- C ----
        d.h1("C. Les heuristiques etalonnees (detail de chacune)")
        d.h2("1. Plus proche voisin depuis le depot")
        d.body("Glouton : depuis le point courant, on va toujours au point non visite le "
               "plus proche. Cout O(n^2). MYOPE : il enchaine des sauts courts, mais a la "
               "fin il ne reste que des points lointains, et surtout l'arete de retour au "
               "depot est subie (souvent longue). Aucune garantie.")
        d.h2("2. Plus proche voisin, meilleur depart")
        d.body("Le PPV depend fortement du point de depart. Parade : le relancer depuis "
               "chacun des n sommets et garder le meilleur tour. Cout O(n^3) — toujours "
               "polynomial.")
        d.body("Garantie theorique (Rosenkrantz-Stearns-Lewis, 1977) pour un TSP "
               "metrique : le tour ne depasse jamais l'optimum d'un facteur")
        formula(d, r"$\frac{1}{2}\left(\lceil \log_{2} n \rceil + 1\right)$",
                size=14, height=0.05)
        d.body("Pour n=14 : 0,5 x (4 + 1) = 2,5, soit jusqu'a +150 % dans le pire cas. "
               "Les ecarts mesures (max +24,8 %) sont bien en dessous : rassurant, mais "
               "garantie faible, d'ou l'interet de raffiner par 2-opt.")
        d.h2("3. 2-opt")
        d.body("On part du meilleur PPV et on l'ameliore : on cherche les croisements et "
               "on les defait (retirer 2 aretes, reconnecter en inversant un segment, si "
               "le gain delta < 0). On repete tant qu'une amelioration existe. Le resultat "
               "est un OPTIMUM LOCAL : aucun echange de 2 aretes ne l'ameliore — mais ce "
               "n'est pas forcement l'optimum GLOBAL. L'etalonnage est precisement la "
               "preuve quantitative que cet optimum local est, en pratique, tres proche "
               "du global.")

        # ---- D ----
        d.h1("D. La methodologie de l'etalonnage (ce que fait step5)")
        d.body("Le script orchestre tout, sans toucher aux fichiers de 43 points :")
        d.bullet("pick_subquartier(coords, anchor, size) : construit un sous-quartier "
                 "geographiquement coherent : le depot (indice local 0) + les 13 points "
                 "les plus proches d'une ancre. Les 7 ancres balaient differentes zones "
                 "-> Q1 a Q7.")
        d.bullet("submatrix(coords, idx) : reconstruit la matrice des temps du sous-groupe "
                 "avec EXACTEMENT les memes parametres que step1 (haversine, 30 km/h, "
                 "DETOUR=1.0) -> coherence garantie.")
        d.bullet("symmetrize : pour valider le 2-opt.")
        d.bullet("sur chaque sous-quartier : nn0, nnb, held_karp (= l'optimum), "
                 "two_opt(nnb), puis les 3 ecarts a l'optimum.")
        d.bullet("agregation (moyenne / min / max) sur les 7 sous-quartiers -> la "
                 "distribution.")

        # ---- E ----
        d.h1("E. Lecture fine des resultats")
        xs5 = [0.08, 0.31, 0.50, 0.66, 0.82]
        rowN(d, ["Sous-quartier", "Optimum (HK)", "PPV depot", "PPV best", "2-opt"],
             xs5, header=True)
        for k, r in enumerate(calib, 1):
            two = float(r["ecart_2opt_%"])
            rowN(d, [f"Q{k}", fmt(r["optimum_HK_s"]),
                     f'+{float(r["ecart_ppv_depot_%"]):.1f}%',
                     f'+{float(r["ecart_ppv_best_%"]):.1f}%',
                     f'+{two:.1f}%'], xs5, bold=(two == 0.0))
        d.space(0.012)
        d.body("Distribution agregee :")
        xs4 = [0.08, 0.50, 0.66, 0.80]
        rowN(d, ["Heuristique", "ecart moyen", "min", "max"], xs4, header=True)
        for label, g, hl in [("Plus proche voisin (depot)", g0, False),
                             ("Plus proche voisin (meilleur depart)", gb, False),
                             ("2-opt (sur meilleur PPV)", g2, True)]:
            d._need(0.025)
            color = ACCENT if hl else INK
            w = "bold" if hl else "normal"
            d.fig.text(0.08, d.y, label, fontsize=8.4, color=color, weight=w)
            d.fig.text(0.50, d.y, f"+{statistics.mean(g):.1f} %", fontsize=8.4, color=color, weight=w)
            d.fig.text(0.66, d.y, f"+{min(g):.1f} %", fontsize=8.4, color=color, weight=w)
            d.fig.text(0.80, d.y, f"+{max(g):.1f} %", fontsize=8.4, color=color, weight=w)
            d.y -= 0.025
        d.space(0.012)
        d.h2("Trois observations a defendre")
        d.bullet("2-opt est quasi-optimal : +0,9 % en moyenne, et il atteint l'optimum "
                 "exact sur Q4 et Q6 (+0,0 %), maximum +3,7 %. Argument central : le cout "
                 "de l'optimalite garantie (Held-Karp, exponentiel) n'en vaut pas la "
                 "peine, puisqu'une heuristique polynomiale s'en approche a ~1 %.")
        d.bullet("Le PPV est instable et parfois mauvais : jusqu'a +24,8 % (Q2). Une "
                 "heuristique de construction seule ne suffit pas.")
        d.bullet("Cas instructifs : Q1, Q3, Q4 -> PPV depot = PPV best (le depot etait "
                 "deja le meilleur depart). Q2, Q6, Q7 -> le choix du depart compte "
                 "beaucoup (Q6 : 18,2 % -> 9,7 %). Q1 et Q7 -> 2-opt reste a +3,7 % et "
                 "+1,8 % sans atteindre 0 % : illustration empirique de 'optimum local "
                 "!= optimum global' (section 4.6).")

        # ---- F ----
        d.h1("F. Limites et honnetete (a dire au jury)")
        d.bullet("L'ecart est mesure sur des instances de 14 points ; l'extrapolation a "
                 "43 points est plausible mais NON demontree — a presenter comme une "
                 "estimation prudente, jamais comme une preuve.")
        d.bullet("Les ecarts dependent de l'echantillon de sous-quartiers (7 ici) ; en "
                 "augmenter le nombre resserrerait la distribution.")
        d.bullet("Tout repose sur le mode hypothese (vol d'oiseau, 30 km/h) ; l'ordre "
                 "des ecarts pourrait varier en mode osm — analyse de robustesse encore "
                 "a faire.")

        d.finish()

        insert_image(d, pdf, "calibration_gaps.png",
                     "Figure — Ecart a l'optimum exact par sous-quartier",
                     "Pour chaque sous-quartier (<= 15 points), ecart en % a l'optimum "
                     "Held-Karp. Le 2-opt (rouge) reste colle a 0 % ; le plus proche "
                     "voisin (beige/orange) s'en eloigne nettement.")

    print("PDF ecrit -> annexe_etalonnage_held_karp.pdf")


if __name__ == "__main__":
    main()
