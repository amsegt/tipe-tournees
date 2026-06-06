# -*- coding: utf-8 -*-
"""
make_doc.py — DOCUMENTATION DETAILLEE du projet, pour un lecteur NON programmeur.

Explique, module par module, le role de chaque fichier, de la classe Doc et de
CHAQUE fonction (a quoi elle sert, ce qu'on lui donne, ce qu'elle renvoie),
avec des analogies du quotidien et des schemas.

Genere d'abord les schemas (matplotlib), puis assemble le PDF en reutilisant le
moteur de mise en page de make_report.py.

Sortie : documentation_projet.pdf
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
from make_report import Doc, image_page, PAGE, INK, ACCENT, TEAL, GREEN

FILE_FC = "#EAF3F4"; FILE_EC = "#8FB6BA"
LIB_FC = "#F1ECF7"; LIB_EC = "#B9A7D0"


# ==========================================================================
#  Schemas (dessines avec des rectangles + fleches)
# ==========================================================================
def _box(ax, cx, cy, w, h, text, fc, ec, tc="#1A1A1A", fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.006,rounding_size=0.015",
                                fc=fc, ec=ec, lw=1.3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc,
            weight="bold" if bold else "normal")


def _arrow(ax, x1, y1, x2, y2, color="#666666"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5,
                                shrinkA=2, shrinkB=2))


def _canvas(title):
    fig, ax = plt.subplots(figsize=(10, 6.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title(title, fontsize=13, weight="bold", color=INK, pad=12)
    return fig, ax


def draw_pipeline():
    """Le flux principal : points -> step1 -> step2 -> step3."""
    fig, ax = _canvas("Le flux principal des donnees (etapes 1 a 3)")
    _box(ax, 0.5, 0.93, 0.34, 0.08, "points.geojson\n(tes points GPS)", FILE_FC, FILE_EC, fs=9, bold=True)
    _arrow(ax, 0.5, 0.89, 0.5, 0.85)
    _box(ax, 0.5, 0.80, 0.30, 0.075, "step1_build_matrix.py", TEAL, TEAL, tc="white", bold=True)
    _arrow(ax, 0.5, 0.762, 0.5, 0.72)
    _box(ax, 0.22, 0.67, 0.30, 0.075, "travel_time_matrix.csv\n(tableau des temps)", FILE_FC, FILE_EC, fs=8)
    _box(ax, 0.55, 0.67, 0.20, 0.075, "coords.csv", FILE_FC, FILE_EC, fs=8)
    _box(ax, 0.81, 0.67, 0.26, 0.075, "road_graph.graphml\n(mode osm)", FILE_FC, FILE_EC, fs=8)
    _arrow(ax, 0.22, 0.632, 0.22, 0.59)
    _box(ax, 0.22, 0.545, 0.30, 0.075, "step2_solve.py", GREEN, GREEN, tc="white", bold=True)
    _arrow(ax, 0.22, 0.507, 0.22, 0.465)
    _box(ax, 0.16, 0.415, 0.20, 0.07, "results.csv", FILE_FC, FILE_EC, fs=8)
    _box(ax, 0.40, 0.415, 0.22, 0.07, "best_tour.json", FILE_FC, FILE_EC, fs=8)
    _arrow(ax, 0.40, 0.379, 0.40, 0.335)
    # step3 reads best_tour.json + coords + graphml
    _arrow(ax, 0.55, 0.632, 0.50, 0.335, color="#AAAAAA")
    _arrow(ax, 0.81, 0.632, 0.58, 0.335, color="#AAAAAA")
    _box(ax, 0.45, 0.285, 0.30, 0.075, "step3_plot_map.py", ACCENT, ACCENT, tc="white", bold=True)
    _arrow(ax, 0.45, 0.247, 0.45, 0.205)
    _box(ax, 0.45, 0.155, 0.26, 0.075, "best_tour.png\n(la carte)", FILE_FC, FILE_EC, fs=8, bold=True)
    ax.text(0.5, 0.045, "Bleu = fichier de donnees   •   couleur pleine = programme (script)",
            ha="center", fontsize=8.5, color="#777777", style="italic")
    fig.savefig("doc_pipeline.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def draw_tools():
    """Les outils annexes : step4, step5, make_report / make_results_*."""
    fig, ax = _canvas("Les outils d'analyse et de presentation")
    _box(ax, 0.5, 0.92, 0.2, 0.08, "coords.csv", FILE_FC, FILE_EC, bold=True)
    # step4
    _arrow(ax, 0.42, 0.89, 0.22, 0.80)
    _box(ax, 0.20, 0.74, 0.30, 0.075, "step4_graph.py", TEAL, TEAL, tc="white", bold=True)
    _arrow(ax, 0.20, 0.70, 0.20, 0.655)
    _box(ax, 0.20, 0.60, 0.34, 0.085, "graph_view.png\nadjacency_heatmap.png\nadjacency_matrix_m.csv", FILE_FC, FILE_EC, fs=7.5)
    # step5
    _arrow(ax, 0.58, 0.89, 0.78, 0.80)
    _box(ax, 0.80, 0.74, 0.30, 0.075, "step5_calibrate.py", GREEN, GREEN, tc="white", bold=True)
    _arrow(ax, 0.80, 0.70, 0.80, 0.655)
    _box(ax, 0.80, 0.60, 0.32, 0.075, "calibration_results.csv\ncalibration_gaps.png", FILE_FC, FILE_EC, fs=7.5)
    # report generators
    _box(ax, 0.18, 0.40, 0.30, 0.07, "make_report.py", "#5B7DB1", "#5B7DB1", tc="white", bold=True)
    _arrow(ax, 0.18, 0.365, 0.18, 0.315)
    _box(ax, 0.18, 0.27, 0.24, 0.065, "rapport_tipe.pdf", FILE_FC, FILE_EC, fs=8)
    _box(ax, 0.55, 0.40, 0.34, 0.07, "make_results_report.py", "#5B7DB1", "#5B7DB1", tc="white", bold=True)
    _arrow(ax, 0.55, 0.365, 0.55, 0.315)
    _box(ax, 0.55, 0.27, 0.26, 0.065, "resultats_tipe.pdf", FILE_FC, FILE_EC, fs=8)
    _box(ax, 0.86, 0.40, 0.26, 0.07, "make_results_pptx.py", "#5B7DB1", "#5B7DB1", tc="white", bold=True)
    _arrow(ax, 0.86, 0.365, 0.86, 0.315)
    _box(ax, 0.86, 0.27, 0.24, 0.065, "Resultats_...pptx", FILE_FC, FILE_EC, fs=7.5)
    ax.text(0.5, 0.12, "make_results_report.py et make_results_pptx.py lisent results.csv\n"
                       "et calibration_results.csv pour produire les livrables.",
            ha="center", fontsize=8.5, color="#777777", style="italic")
    fig.savefig("doc_tools.png", dpi=200, bbox_inches="tight"); plt.close(fig)


def draw_modules():
    """Carte des dependances : qui utilise quoi."""
    fig, ax = _canvas("Carte des modules : qui s'appuie sur quoi")
    _box(ax, 0.5, 0.5, 0.26, 0.12, "tsp_core.py\nles 3 algorithmes\n(le moteur de calcul)",
         ACCENT, ACCENT, tc="white", fs=9.5, bold=True)
    _box(ax, 0.18, 0.82, 0.24, 0.08, "step2_solve.py", GREEN, GREEN, tc="white", bold=True)
    _box(ax, 0.82, 0.82, 0.24, 0.08, "step5_calibrate.py", GREEN, GREEN, tc="white", bold=True)
    _arrow(ax, 0.24, 0.78, 0.43, 0.56)
    _arrow(ax, 0.76, 0.78, 0.57, 0.56)
    ax.text(0.30, 0.69, "utilise", fontsize=8, color="#888", style="italic")
    ax.text(0.66, 0.69, "utilise", fontsize=8, color="#888", style="italic")
    # external libs
    _box(ax, 0.5, 0.16, 0.62, 0.08,
         "bibliotheques externes : matplotlib (dessin) • networkx (graphes) • osmnx (cartes) • numpy",
         LIB_FC, LIB_EC, fs=8)
    for x in (0.18, 0.82):
        _arrow(ax, x, 0.78, 0.5, 0.205, color="#CBBEDD")
    _arrow(ax, 0.5, 0.44, 0.5, 0.205, color="#CBBEDD")
    # report deps
    _box(ax, 0.5, 0.93, 0.56, 0.085,
         "make_results_report.py + make_results_pptx.py\nreutilisent make_report.py",
         "#5B7DB1", "#5B7DB1", tc="white", fs=8.5)
    fig.savefig("doc_modules.png", dpi=200, bbox_inches="tight"); plt.close(fig)


# ==========================================================================
#  Helpers de redaction
# ==========================================================================
def insert_image(d, pdf, path, title, caption):
    """Vide la page de texte courante, insere une page-image, repart a neuf."""
    if d.fig is not None:
        d._flush()
    image_page(pdf, path, title, caption)
    d._new_page()


def card(d, name, role, entree, sortie, comment=None, code=None):
    """Fiche uniforme decrivant une fonction."""
    d.h2(name)
    d.body("A quoi ca sert : " + role)
    d.bullet("Entree (ce qu'on lui donne) : " + entree)
    d.bullet("Sortie (ce qu'elle renvoie) : " + sortie)
    if comment:
        d.body("En clair : " + comment)
    if code:
        d.code(code)


def cover(pdf):
    fig = plt.figure(figsize=PAGE)
    fig.add_artist(plt.Rectangle((0, 0.80), 1, 0.20, color=TEAL, transform=fig.transFigure))
    fig.text(0.5, 0.90, "Documentation detaillee du projet", ha="center", va="center",
             fontsize=21, weight="bold", color="white")
    fig.text(0.5, 0.855, "TIPE 13530 — Optimisation des tournees de collecte",
             ha="center", va="center", fontsize=12.5, color="white")
    fig.text(0.5, 0.64,
             "Comprendre chaque fichier, chaque classe et chaque fonction\n"
             "du programme — meme sans savoir coder.",
             ha="center", va="center", fontsize=13, color=INK)
    fig.text(0.5, 0.45,
             "Chaque fonction est expliquee par : a quoi elle sert,\n"
             "ce qu'on lui donne (entree), ce qu'elle renvoie (sortie),\n"
             "et une explication en langage courant.",
             ha="center", va="center", fontsize=11.5, color="#444444")
    fig.text(0.5, 0.07, "Genere par make_doc.py", ha="center", va="center",
             fontsize=8.5, color="#999999", style="italic")
    pdf.savefig(fig); plt.close(fig)


# ==========================================================================
#  Le document
# ==========================================================================
def main():
    draw_pipeline(); draw_tools(); draw_modules()

    with PdfPages("documentation_projet.pdf") as pdf:
        cover(pdf)
        d = Doc(pdf)

        # ---- 0. Pour le lecteur non programmeur ----
        d.h1("0. A lire d'abord (si vous ne codez pas)")
        d.body("Ce document explique un PROGRAMME. Pour le comprendre, six mots "
               "suffisent. On les illustre avec l'image d'une cuisine.")
        d.bullet("Un PROGRAMME est comme un grand livre de recettes : une suite "
                 "d'instructions qui transforment des ingredients en plat.")
        d.bullet("Un FICHIER (ou module) est un chapitre du livre : il regroupe "
                 "des recettes qui vont ensemble (ex. tsp_core.py = le chapitre des algorithmes).")
        d.bullet("Une FONCTION est une recette precise : on lui donne des ingredients, "
                 "elle rend un plat. Ex. 'longueur d'un tour' : on lui donne un trajet, "
                 "elle rend sa duree totale.")
        d.bullet("Un PARAMETRE (ou argument) est un ingredient qu'on fournit a la recette.")
        d.bullet("La VALEUR DE RETOUR est le plat fini que la recette rend a la fin.")
        d.bullet("Une CLASSE est un APPAREIL de cuisine (ex. un robot) : un objet qui "
                 "retient un etat (ce qu'il contient) et possede des boutons (ses METHODES). "
                 "Ce projet n'a qu'une seule classe, Doc, expliquee en section 9.")
        d.space()
        d.body("Trois structures de donnees reviennent souvent :")
        d.bullet("une LISTE = une liste de courses ordonnee : [A, B, C]. On peut lire "
                 "le 1er, le 2e element, etc.")
        d.bullet("un DICTIONNAIRE = un meuble a tiroirs etiquetes : a l'etiquette "
                 "'temps' correspond un contenu. On range et on retrouve par etiquette.")
        d.bullet("une MATRICE = un tableau a double entree, comme la table des "
                 "kilometrages d'une carte routiere : la case (ligne i, colonne j) "
                 "donne le temps pour aller du point i au point j.")
        d.bullet("un FICHIER CSV = un tableur (type Excel) en texte simple : des "
                 "lignes et des colonnes separees par des virgules.")

        # ---- 1. Vue d'ensemble ----
        d.h1("1. Vue d'ensemble du projet")
        d.body("Le but : partir d'une liste de points a collecter et trouver la "
               "tournee (le cycle) la plus rapide qui les visite tous puis revient "
               "au depot. Le projet enchaine des etapes, chacune dans son fichier ; "
               "chaque etape ecrit des fichiers que la suivante relit.")
        d.body("Le schema ci-apres montre le flux principal : un fichier de points "
               "entre, une carte du meilleur trajet sort.")
        insert_image(d, pdf, "doc_pipeline.png",
                     "Schema 1 — Le flux principal des donnees",
                     "On lit de haut en bas : points.geojson -> step1 fabrique la "
                     "matrice des temps -> step2 calcule le meilleur tour -> step3 "
                     "le dessine. Les boites bleues sont des fichiers, les boites "
                     "colorees sont des programmes.")
        d.body("A cote de ce flux principal, des OUTILS analysent et presentent les "
               "resultats : step4 (graphe + matrice), step5 (etalonnage), et trois "
               "generateurs de rapports.")
        insert_image(d, pdf, "doc_tools.png",
                     "Schema 2 — Les outils d'analyse et de presentation",
                     "step4 et step5 lisent coords.csv. Les generateurs de rapports "
                     "lisent les fichiers de resultats et produisent les PDF et le PPT.")
        insert_image(d, pdf, "doc_modules.png",
                     "Schema 3 — Carte des modules (qui utilise quoi)",
                     "tsp_core.py est le moteur de calcul : step2 et step5 s'appuient "
                     "dessus. Tout le monde s'appuie sur des bibliotheques externes.")

        # ---- 2. tsp_core ----
        d.h1("2. tsp_core.py — le moteur : les 3 algorithmes")
        d.body("C'est le coeur mathematique. Il ne dessine rien, ne lit pas Internet : "
               "il prend une matrice de temps et calcule des tournees. Image : une "
               "boite a outils de calcul, utilisee par d'autres fichiers.")
        card(d, "read_matrix_csv(path)",
             "lire la matrice des temps depuis un fichier tableur (CSV).",
             "le nom du fichier a lire.",
             "la matrice (tableau de nombres) chargee en memoire.",
             "elle ouvre le tableur, transforme chaque texte en nombre, et verifie "
             "que le tableau est bien carre (autant de lignes que de colonnes).")
        card(d, "symmetrize(D)",
             "rendre la matrice symetrique : aller de i a j coute autant que de j a i.",
             "une matrice D (eventuellement asymetrique a cause des sens uniques).",
             "une nouvelle matrice ou chaque case est la moyenne des deux sens.",
             "T[i][j] devient (T[i][j] + T[j][i]) / 2. C'est une hypothese de "
             "modelisation, necessaire pour que l'algorithme 2-opt soit valable.")
        card(d, "tour_length(tour, D)",
             "mesurer la duree totale d'une tournee donnee.",
             "un tour (l'ordre de visite des points) et la matrice des temps D.",
             "un seul nombre : la somme des temps de toutes les etapes, retour au depart inclus.",
             "elle additionne le temps de chaque saut consecutif du trajet, puis "
             "ajoute le retour du dernier point vers le depart.")
        card(d, "nearest_neighbor(D, start=0)",
             "construire une tournee par la regle du PLUS PROCHE VOISIN (algorithme 1).",
             "la matrice des temps et le point de depart.",
             "un tour (liste ordonnee des points).",
             "depuis le point courant, on va toujours vers le point non encore visite "
             "le plus proche, jusqu'a les avoir tous visites. Rapide mais 'myope'.",
             "for _ in range(n-1):\n    j = le plus proche non visite\n    on va en j")
        card(d, "nearest_neighbor_best_start(D)",
             "ameliorer l'algorithme 1 en essayant TOUS les departs.",
             "la matrice des temps.",
             "le meilleur tour obtenu parmi tous les points de depart possibles.",
             "le plus proche voisin depend du point de depart ; on le relance depuis "
             "chaque point et on garde le meilleur resultat.")
        card(d, "two_opt(tour, D)",
             "ameliorer une tournee existante par 2-OPT (algorithme 2).",
             "un tour de depart et la matrice des temps.",
             "un tour ameliore (un 'optimum local').",
             "on cherche les croisements du trajet et on les 'decroise' : on retire "
             "deux segments et on les rebranche autrement si cela raccourcit le tour. "
             "On repete tant qu'on trouve une amelioration.")
        card(d, "held_karp(D)",
             "trouver la tournee EXACTEMENT optimale (algorithme 3, Held-Karp).",
             "la matrice des temps (petites instances seulement).",
             "un couple : le meilleur tour et son cout exact.",
             "par programmation dynamique : on calcule le meilleur chemin pour chaque "
             "petit groupe de points, puis on assemble les grands a partir des petits. "
             "Garanti optimal, mais devient impossible au-dela d'environ 20 points.")
        card(d, "_subsets(elems, k)",
             "fonction auxiliaire de Held-Karp : lister tous les groupes de k points.",
             "une collection d'elements et une taille k.",
             "tous les sous-groupes possibles de taille k, un par un.",
             "le tiret bas '_' devant le nom signale une fonction 'interne', utilisee "
             "seulement par held_karp, pas destinee a l'utilisateur.")
        card(d, "brute_force(D)",
             "verification : essayer TOUTES les tournees possibles (force brute).",
             "la matrice des temps (tres petites instances seulement).",
             "le meilleur tour et son cout.",
             "elle enumere les (n-1)! ordres possibles. Sert uniquement a verifier que "
             "Held-Karp donne bien le meme optimum. Inutilisable au-dela de ~10 points.")

        # ---- 3. step1 ----
        d.h1("3. step1_build_matrix.py — fabriquer la matrice des temps")
        d.body("Cette etape transforme tes points GPS en une matrice de temps de "
               "trajet, que tout le reste utilisera. Deux methodes possibles.")
        card(d, "haversine_m(lat1, lon1, lat2, lon2)",
             "calculer la distance 'a vol d'oiseau' entre deux points GPS.",
             "les coordonnees (latitude, longitude) de deux points.",
             "la distance en metres.",
             "la Terre est ronde : cette formule (haversine) donne la vraie distance "
             "sur la sphere, pas sur une carte plate.")
        card(d, "load_points(path)",
             "lire tes points depuis le fichier points.geojson.",
             "le nom du fichier de points.",
             "la liste des coordonnees (longitude, latitude) de chaque point.",
             "le tout PREMIER point du fichier est considere comme le depot "
             "(depart et arrivee de la tournee).")
        card(d, "build_matrix_hypothesis(coords)",
             "construire la matrice des temps avec l'HYPOTHESE FORTE.",
             "la liste des coordonnees des points.",
             "la matrice des temps + le temps moyen entre deux points.",
             "temps = distance a vol d'oiseau / vitesse constante (30 km/h par defaut). "
             "Simple et instantane, mais ignore les vraies routes.")
        card(d, "build_matrix_osm(coords)",
             "construire la matrice avec le VRAI reseau routier (mode osm).",
             "la liste des coordonnees.",
             "la matrice des temps reels + sauvegarde du reseau routier.",
             "elle telecharge les rues autour de tes points (via Internet/OSMnx) et "
             "calcule le plus court chemin reel entre chaque paire. Plus fidele, plus lourd.")
        card(d, "fmt(sec)",
             "afficher joliment une duree en secondes.",
             "un nombre de secondes.",
             "un texte lisible comme '13min23s'.",
             "petit utilitaire de presentation, present aussi dans d'autres fichiers.")
        card(d, "main()",
             "le chef d'orchestre du fichier : enchaine tout quand on lance step1.",
             "rien (il lit les parametres en haut du fichier).",
             "rien, mais ecrit les fichiers de sortie sur le disque.",
             "il lit les points, choisit la methode, construit la matrice, affiche un "
             "resume et sauvegarde travel_time_matrix.csv et coords.csv.")

        # ---- 4. step2 ----
        d.h1("4. step2_solve.py — resoudre et comparer")
        d.body("Cette etape lit la matrice et lance les trois algorithmes pour les "
               "comparer. Elle s'appuie entierement sur tsp_core.py.")
        card(d, "fmt(sec)",
             "meme utilitaire d'affichage de duree que dans step1.",
             "un nombre de secondes.", "un texte lisible.",
             "duplique ici pour que le fichier reste autonome.")
        card(d, "main()",
             "lancer PPV, PPV-meilleur-depart, 2-opt et (si possible) Held-Karp, "
             "puis comparer.",
             "rien (lit la matrice sur le disque).",
             "affiche un tableau comparatif et ecrit results.csv et best_tour.json.",
             "il mesure pour chaque methode le temps de cycle ET le temps de calcul, "
             "calcule l'ecart a l'optimum si Held-Karp a tourne, et retient le meilleur tour.")

        # ---- 5. step3 ----
        d.h1("5. step3_plot_map.py — dessiner le meilleur tour")
        card(d, "load_coords(path)",
             "relire les coordonnees des points depuis coords.csv.",
             "le nom du fichier.", "la liste des points (longitude, latitude).",
             "necessaire pour savoir ou placer chaque point sur le dessin.")
        card(d, "plot_streets(order, coords)",
             "tracer l'itineraire reel le long des rues (si le reseau est disponible).",
             "l'ordre de visite et les coordonnees.",
             "une image best_tour.png suivant les vraies routes.",
             "utilise le reseau routier sauvegarde par step1 en mode osm.")
        card(d, "plot_schema(order, coords)",
             "tracer un schema simple : points relies par des segments droits.",
             "l'ordre de visite et les coordonnees.",
             "une image best_tour.png schematique.",
             "solution de secours quand le reseau routier n'est pas disponible "
             "(comme en mode hypothese) : montre l'ordre de visite, pas les rues.")
        card(d, "main()",
             "choisir automatiquement entre rues reelles et schema, puis dessiner.",
             "rien.", "l'image best_tour.png.",
             "s'il existe un reseau routier, il tente les rues ; sinon il retombe sur le schema.")

        # ---- 6. step4 ----
        d.h1("6. step4_graph.py — graphe pondere + matrice d'adjacence")
        d.body("Cet outil represente tes points comme un GRAPHE (des points relies "
               "par des traits etiquetes de distances) et affiche la matrice complete.")
        card(d, "haversine_m(...)", "meme calcul de distance a vol d'oiseau qu'en step1.",
             "deux points GPS.", "la distance en metres.", None)
        card(d, "load_coords()", "lire les points depuis coords.csv (ou le GeoJSON en secours).",
             "rien.", "la liste des points.", None)
        card(d, "distance_matrix(coords)",
             "construire la matrice des distances (en metres) entre tous les points.",
             "la liste des points.", "la matrice n x n des distances.",
             "c'est la matrice d'adjacence du graphe complet : toutes les paires.")
        card(d, "label_of(d_m)", "formater une distance pour l'ecrire sur une arete.",
             "une distance en metres.", "un texte court (metres ou kilometres).", None)
        card(d, "build_graph(coords, D)",
             "construire l'objet graphe (avec networkx) a dessiner.",
             "les points et la matrice des distances.",
             "un graphe ou chaque point est relie a ses plus proches voisins.",
             "on ne relie que les plus proches voisins pour que le dessin reste lisible.")
        card(d, "plot_graph(coords, D, G)",
             "dessiner le graphe : points a leur place reelle, distances sur les traits.",
             "les points, la matrice et le graphe.", "l'image graph_view.png.", None)
        card(d, "plot_heatmap(D)",
             "dessiner la matrice complete en carte de chaleur (couleurs).",
             "la matrice des distances.", "l'image adjacency_heatmap.png.",
             "sombre = proche, clair = lointain ; revele les groupes de points.")
        card(d, "save_and_preview_matrix(D)",
             "sauvegarder la matrice en CSV et en montrer un coin a l'ecran.",
             "la matrice.", "le fichier adjacency_matrix_m.csv + un apercu affiche.", None)
        insert_image(d, pdf, "graph_view.png",
                     "Sortie de step4 — le graphe pondere",
                     "Les points a leur position reelle ; chaque trait porte la distance "
                     "en metres. Le carre est le depot.")
        insert_image(d, pdf, "adjacency_heatmap.png",
                     "Sortie de step4 — la matrice d'adjacence",
                     "La meme information, vue comme un tableau de couleurs 43x43.")

        # ---- 7. step5 ----
        d.h1("7. step5_calibrate.py — etalonner les heuristiques")
        d.body("Cet outil mesure la QUALITE des heuristiques en les comparant a "
               "l'optimum exact (Held-Karp) sur de petits sous-quartiers.")
        card(d, "haversine_m(...) / load_coords()",
             "memes utilitaires que precedemment (distance, lecture des points).",
             "points GPS / rien.", "distance / liste de points.", None)
        card(d, "submatrix(coords, idx)",
             "construire la matrice des temps d'un sous-groupe de points.",
             "tous les points et la liste des indices choisis.",
             "la petite matrice des temps de ce sous-quartier.", None)
        card(d, "pick_subquartier(coords, anchor, size)",
             "choisir un sous-quartier coherent : le depot + les voisins d'un point d'ancrage.",
             "les points, un point d'ancrage, la taille voulue.",
             "la liste des indices du sous-quartier (depot en premier).",
             "on prend les points geographiquement proches de l'ancrage, pour un "
             "sous-quartier realiste.")
        card(d, "fmt(sec)", "afficher une duree lisiblement.", "des secondes.", "un texte.", None)
        card(d, "main()",
             "lancer l'etalonnage sur plusieurs sous-quartiers et agreger les ecarts.",
             "rien.",
             "un tableau d'ecarts a l'optimum, calibration_results.csv et calibration_gaps.png.",
             "pour chaque sous-quartier, il calcule l'optimum exact et mesure de combien "
             "de % chaque heuristique s'en ecarte, puis resume la distribution.")
        insert_image(d, pdf, "calibration_gaps.png",
                     "Sortie de step5 — l'etalonnage",
                     "Ecart a l'optimum exact, par sous-quartier. Le 2-opt (rouge) reste "
                     "quasiment a 0 % : il est presque toujours optimal.")

        # ---- 8. make_report ----
        d.h1("8. make_report.py — fabriquer le rapport PDF")
        d.body("Ce fichier fabrique un PDF. Il contient la SEULE vraie classe du "
               "projet : la classe Doc. On l'explique en detail.")
        d.h2("La classe Doc — une 'machine a ecrire des pages'")
        d.body("Rappel : une classe est un appareil qui retient un etat et a des "
               "boutons (methodes). La classe Doc retient la page en cours et la "
               "position du curseur (ou ecrire la prochaine ligne), et descend "
               "automatiquement ; quand la page est pleine, elle en commence une nouvelle.")
        d.body("Ses methodes (ses 'boutons') :")
        d.bullet("__init__ : l'allumage. Cree la machine et prepare la premiere page.")
        d.bullet("_new_page : commencer une page vierge (et sauver la precedente).")
        d.bullet("_flush : enregistrer la page courante dans le PDF.")
        d.bullet("_need(h) : verifier qu'il reste assez de place ; sinon, page suivante.")
        d.bullet("_line : ecrire une ligne et descendre le curseur.")
        d.bullet("h1 / h2 : ecrire un grand / moyen titre.")
        d.bullet("body : ecrire un paragraphe (avec retour a la ligne automatique).")
        d.bullet("bullet : ecrire un point de liste (avec une puce).")
        d.bullet("code : ecrire un extrait de code en police a chasse fixe.")
        d.bullet("space : laisser un espace vertical.")
        d.bullet("finish : enregistrer la derniere page (on a fini d'ecrire).")
        d.space()
        d.body("Les autres fonctions de make_report.py :")
        card(d, "image_page(pdf, path, title, caption)",
             "ajouter une page entiere contenant une image + un titre + une legende.",
             "le PDF, le chemin de l'image, un titre, une legende.",
             "une page ajoutee au PDF.", None)
        card(d, "read_results() / n_points()",
             "lire le tableau de resultats / compter les points.",
             "rien.", "les donnees a afficher dans le rapport.", None)
        card(d, "cover(pdf) / main()",
             "dessiner la couverture / assembler tout le rapport.",
             "le PDF.", "le fichier rapport_tipe.pdf complet.", None)

        # ---- 9. make_results_* ----
        d.h1("9. make_results_report.py & make_results_pptx.py")
        d.body("Ces deux fichiers presentent les RESULTATS (instance 43 points + "
               "etalonnage). Le premier produit un PDF, le second un diaporama "
               "PowerPoint. Tous deux relisent results.csv et calibration_results.csv "
               "et reutilisent des briques de make_report.py.")
        card(d, "fmt / read_results / read_calibration / read_csv",
             "utilitaires : formater une duree, lire les fichiers de resultats.",
             "des secondes / des noms de fichiers.",
             "un texte lisible / des tableaux de donnees.", None)
        card(d, "cover / title slide",
             "fabriquer la page (ou diapo) de titre.",
             "le document.", "la couverture.", None)
        card(d, "results_table / calib_table",
             "dessiner les tableaux de chiffres (resultats et ecarts).",
             "les donnees lues.", "un tableau mis en forme dans la diapo.", None)
        card(d, "add_image_fit / image_page / caption / bullets",
             "placer une image au bon format, ajouter une legende, ecrire des puces.",
             "image et textes.", "des elements ajoutes a la page/diapo.", None)
        card(d, "main()",
             "assembler le livrable complet (PDF ou PPTX).",
             "rien.", "resultats_tipe.pdf ou Resultats_TIPE_13530.pptx.", None)

        # ---- 10. recapitulatif ----
        d.h1("10. Recapitulatif : quel fichier pour quoi")
        d.bullet("tsp_core.py : les 3 algorithmes (le calcul pur).")
        d.bullet("step1 : points -> matrice des temps.")
        d.bullet("step2 : matrice -> comparaison des algorithmes.")
        d.bullet("step3 : meilleur tour -> carte.")
        d.bullet("step4 : points -> graphe + matrice d'adjacence.")
        d.bullet("step5 : etalonnage des heuristiques contre l'optimum exact.")
        d.bullet("make_report : documentation/rapport PDF (contient la classe Doc).")
        d.bullet("make_results_report / make_results_pptx : presentation des resultats (PDF + PPT).")
        d.bullet("make_doc : CE document.")

        d.finish()

    print("PDF ecrit -> documentation_projet.pdf")


if __name__ == "__main__":
    main()
