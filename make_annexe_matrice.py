# -*- coding: utf-8 -*-
"""
make_annexe_matrice.py — ANNEXE TECHNIQUE dediee :
    "De la donnee GeoJSON a la matrice d'adjacence".

Formalise toute la chaine coordonnees -> modelisation -> metrique -> matrice :
formules (haversine, temps), calcul chiffre verifiable sur les points 0 et 1,
proprietes de la matrice, et choix methodologiques.

Formules rendues via le moteur mathtext de matplotlib (pas de LaTeX a installer).
Reutilise le moteur de mise en page de make_report.py.

Sortie : annexe_matrice_adjacence.pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
from make_report import Doc, image_page, PAGE, INK, ACCENT, TEAL, GREEN

FILE_FC = "#EAF3F4"; FILE_EC = "#8FB6BA"


# ---- schema de la chaine de transformation d'une arete -------------------
def _box(ax, cx, cy, w, h, text, fc, ec, tc="#1A1A1A", fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.006,rounding_size=0.02",
                                fc=fc, ec=ec, lw=1.3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=tc,
            weight="bold" if bold else "normal")


def _arrow(ax, x1, y1, x2, y2, color="#666666"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6))


def draw_chain():
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("Chaine de transformation d'UNE arete : du couple GPS au poids",
                 fontsize=12, weight="bold", color=INK, pad=8)
    y = 0.60
    _box(ax, 0.10, y, 0.16, 0.34, "2 points GPS\n(lon, lat)", FILE_FC, FILE_EC, fs=8.5, bold=True)
    _arrow(ax, 0.185, y, 0.225, y)
    _box(ax, 0.31, y, 0.16, 0.34, "haversine_m()", TEAL, TEAL, tc="white", fs=9, bold=True)
    _arrow(ax, 0.395, y, 0.435, y)
    _box(ax, 0.52, y, 0.16, 0.34, "distance\n79,3 m", FILE_FC, FILE_EC, fs=8.5)
    _arrow(ax, 0.605, y, 0.645, y)
    _box(ax, 0.73, y, 0.16, 0.34, "x DETOUR\n/ vitesse", ACCENT, ACCENT, tc="white", fs=8.5, bold=True)
    _arrow(ax, 0.815, y, 0.855, y)
    _box(ax, 0.93, y, 0.13, 0.34, "temps\n9,5 s", FILE_FC, FILE_EC, fs=8.5, bold=True)
    ax.text(0.5, 0.13, "Resultat : la case D[0][1] de la matrice d'adjacence "
                       "(ici en secondes ; en metres pour step4).",
            ha="center", fontsize=9, color="#666666", style="italic")
    fig.savefig("annexe_chaine.png", dpi=200, bbox_inches="tight"); plt.close(fig)


# ---- helpers de redaction ------------------------------------------------
def formula(d, tex, size=14, height=0.045):
    """Ecrit une formule centree (mathtext)."""
    d.space(0.006)
    d._need(height + 0.012)
    d.fig.text(0.5, d.y, tex, fontsize=size, color=INK, ha="center", va="top")
    d.y -= height
    d.space(0.008)


def row3(d, c1, c2, c3, bold=False, header=False):
    d._need(0.026)
    color = TEAL if header else INK
    w = "bold" if (bold or header) else "normal"
    d.fig.text(0.08, d.y, c1, fontsize=8.7, color=color, weight=w)
    d.fig.text(0.40, d.y, c2, fontsize=8.7, color=color, weight=w)
    d.fig.text(0.67, d.y, c3, fontsize=8.7, color=color, weight=w)
    d.y -= 0.026


def insert_image(d, pdf, path, title, caption):
    if d.fig is not None:
        d._flush()
    image_page(pdf, path, title, caption)
    d._new_page()


def cover(pdf):
    fig = plt.figure(figsize=PAGE)
    fig.add_artist(plt.Rectangle((0, 0.80), 1, 0.20, color=TEAL, transform=fig.transFigure))
    fig.text(0.5, 0.905, "Annexe technique", ha="center", va="center",
             fontsize=22, weight="bold", color="white")
    fig.text(0.5, 0.855, "De la donnee GeoJSON a la matrice d'adjacence",
             ha="center", va="center", fontsize=14, color="white")
    fig.text(0.5, 0.66,
             "Comment, a partir des coordonnees, on modelise les points\n"
             "du graphe et on construit la matrice d'adjacence :\n"
             "metriques, calculs chiffres et choix methodologiques.",
             ha="center", va="center", fontsize=12.5, color=INK)
    fig.text(0.5, 0.47,
             "TIPE 13530 — Optimisation des tournees de collecte (Meknes)\n"
             "Brahim Amsegt — CPGE MP — session 2026",
             ha="center", va="center", fontsize=11.5, color="#444444")
    fig.text(0.5, 0.30,
             "Document de travail : tous les nombres chiffres sont recalcules\n"
             "sur les vrais points et peuvent etre verifies a la main.",
             ha="center", va="center", fontsize=10.5, color=ACCENT, style="italic")
    fig.text(0.5, 0.07, "Genere par make_annexe_matrice.py", ha="center", va="center",
             fontsize=8.5, color="#999999", style="italic")
    pdf.savefig(fig); plt.close(fig)


# ==========================================================================
def main():
    draw_chain()

    with PdfPages("annexe_matrice_adjacence.pdf") as pdf:
        cover(pdf)
        d = Doc(pdf)

        d.h1("Vue d'ensemble de la chaine")
        d.body("L'objectif de cette annexe : detailler le maillon 'donnees -> graphe', "
               "c'est-a-dire comment un fichier de points GPS (GeoJSON) devient la "
               "matrice d'adjacence n x n sur laquelle tournent les algorithmes. La "
               "transformation d'une seule arete se resume ainsi :")
        insert_image(d, pdf, "annexe_chaine.png",
                     "Schema — la chaine de transformation d'une arete",
                     "Deux points GPS -> distance (haversine) -> poids temps (/ vitesse). "
                     "Repete pour toutes les paires, cela remplit la matrice d'adjacence.")

        # ---- 1 ----
        d.h1("1. Le point de depart : lire le GeoJSON")
        d.body("Un fichier GeoJSON decrit des entites geographiques en texte. Chaque "
               "point de collecte est une entite 'Point' portant un couple de "
               "coordonnees. La fonction load_points() ne garde que les geometries "
               "'Point' et en extrait les coordonnees :")
        d.code('lon, lat = geom["coordinates"][0], geom["coordinates"][1]\n'
               'coords.append((lon, lat))')
        d.body("Deux choix methodologiques decisifs des cette ligne :")
        d.bullet("L'ordre [longitude, latitude] (et NON l'inverse). C'est la convention "
                 "GeoJSON, contre-intuitive car on dit 'lat/long' a l'oral. Une inversion "
                 "placerait les points a des kilometres : c'est l'erreur classique du domaine.")
        d.bullet("Le PREMIER point du fichier = le depot (indice 0). Ce n'est pas une "
                 "donnee du GeoJSON mais une convention imposee : le sommet 0 a un statut "
                 "particulier (depart fixe de Held-Karp, depart par defaut du PPV).")
        d.body("Resultat : une liste ordonnee de 43 couples (lon, lat). C'est l'ensemble "
               "V des sommets du graphe G = (V, E, w).")

        # ---- 2 ----
        d.h1("2. La modelisation : du point GPS au sommet")
        d.body("Les 43 points GPS deviennent les 43 sommets V. On pose ensuite que le "
               "graphe est COMPLET : entre toute paire de points il existe une arete "
               "(un trajet possible), dont le poids resume tout l'itineraire reel par un "
               "seul nombre. Nombre d'aretes : 43 x 42 / 2 = 903.")
        d.body("C'est pour cela que le DESSIN ne peut pas toutes les montrer lisiblement, "
               "mais que la MATRICE D'ADJACENCE, elle, les contient toutes.")

        # ---- 3 ----
        d.h1("3. La metrique : la formule de haversine (et pas Pythagore)")
        d.body("Pour peser une arete il faut une distance entre deux points GPS. On ne "
               "peut PAS appliquer Pythagore directement sur (lon, lat) : la latitude et "
               "la longitude sont des ANGLES, pas des metres ; et 1 degre de longitude ne "
               "vaut pas la meme distance que 1 degre de latitude (les meridiens se "
               "resserrent vers les poles).")
        d.body("La fonction haversine_m() calcule la distance orthodromique (plus court "
               "arc sur la sphere terrestre) :")
        formula(d, r"$a=\sin^{2}\!\left(\frac{\Delta\varphi}{2}\right)"
                   r"+\cos\varphi_{1}\,\cos\varphi_{2}\,"
                   r"\sin^{2}\!\left(\frac{\Delta\lambda}{2}\right)$", size=15, height=0.055)
        formula(d, r"$d = 2R\,\arcsin\!\left(\sqrt{a}\right)$", size=15, height=0.05)
        d.body("ou phi = latitude (rad), lambda = longitude (rad), R = 6 371 000 m "
               "(rayon terrestre moyen). Le terme cos(phi1).cos(phi2) est exactement ce "
               "qui corrige le resserrement des meridiens.")

        # ---- 4 ----
        d.h1("4. Calcul detaille sur les points 0 et 1 (verifiable)")
        row3(d, "Point", "longitude", "latitude", header=True)
        row3(d, "0 (depot)", "-5,5748658", "33,8617128")
        row3(d, "1", "-5,5752357", "33,8623562")
        d.space(0.008)
        d.body("Etapes du calcul (a suivre une fois, calculatrice en main) :")
        d.code("dphi = 0,00064335 deg = 1,1228e-5 rad\n"
               "dlmb = -0,00036993 deg = -6,457e-6 rad\n"
               "sin^2(dphi/2)                 = 3,152e-11\n"
               "cos f1 . cos f2 . sin^2(dlmb/2) = 0,719e-11\n"
               "a    = 3,871e-11      sqrt(a) = 6,222e-6\n"
               "d    = 2 . 6 371 000 . 6,222e-6 = 79,3 m")
        d.body("C'est exactement la valeur de la case (0,1) de la matrice (l'apercu "
               "affichait 79).")
        d.h2("Verification croisee : le 'plan local'")
        d.body("A cette latitude : 1 deg lat ~ 111,0 km ; 1 deg lon ~ 111,0 x cos(33,86) "
               "~ 92,2 km. Donc :")
        d.bullet("deplacement Nord : 0,00064335 x 111 000 = 71,4 m")
        d.bullet("deplacement Est  : 0,00036993 x 92 200 = 34,1 m")
        formula(d, r"$\sqrt{71{,}4^{2} + 34{,}1^{2}} = 79{,}1\ \mathrm{m}$", size=14, height=0.05)
        d.body("Les deux methodes coincident a l'echelle d'un quartier : cela prouve que "
               "haversine fait bien le travail sans projection manuelle. C'est un argument "
               "de robustesse a montrer au jury.")

        # ---- 5 ----
        d.h1("5. Le poids de l'arete : de la distance au temps")
        d.body("Choix central de la MCOT : le poids est un TEMPS, pas une distance, car "
               "deux trajets de meme longueur peuvent prendre des temps tres differents. "
               "Dans build_matrix_hypothesis() :")
        d.code("v_ms    = AVG_SPEED_KMH / 3.6        # 30 km/h -> 8,333 m/s\n"
               "d       = haversine_m(...) * DETOUR_FACTOR\n"
               "T[i][j] = d / v_ms                   # temps = distance / vitesse")
        formula(d, r"$t(u,v) = \frac{d(u,v)\,\cdot\,\mathrm{DETOUR}}{\bar{v}}$",
                size=15, height=0.055)
        d.body("Sur l'arete 0->1 :  t(0,1) = 79,3 x 1,0 / 8,333 = 9,5 s.")
        d.body("C'est la version 'hypothese forte' de la formule MCOT "
               "t = d / v(type_voie) + penalite, simplifiee par deux hypotheses assumees :")
        d.bullet("AVG_SPEED_KMH = 30 : une vitesse moyenne CONSTANTE (on neglige les "
                 "types de voie). C'est l'hypothese forte a defendre.")
        d.bullet("DETOUR_FACTOR = 1,0 : distance a vol d'oiseau PURE. Le passer a ~1,3 "
                 "relacherait l'hypothese en approchant les detours routiers (un trajet "
                 "reel est ~30 % plus long que la ligne droite). C'est le bouton de realisme.")

        # ---- 6 ----
        d.h1("6. Construire la matrice n x n complete")
        d.body("On remplit un tableau carre D par une double boucle sur toutes les paires :")
        d.code("for i in range(n):\n"
               "    for j in range(n):\n"
               "        if i != j:\n"
               "            d = haversine_m(...) * DETOUR_FACTOR\n"
               "            T[i][j] = d / v_ms")
        d.body("(En step4, distance_matrix() fait pareil mais s'arrete en metres et "
               "exploite la symetrie : seul le triangle superieur est calcule puis recopie.)")
        d.body("Trois proprietes mathematiques garanties par cette construction :")
        row3(d, "Propriete", "Pourquoi", "Consequence", header=True)
        row3(d, "Diagonale nulle D[i][i]=0", "point vers lui-meme", "le if i!=j la laisse a 0")
        row3(d, "Symetrie D[i][j]=D[j][i]", "haversine symetrique", "graphe non oriente")
        row3(d, "Inegalite triangulaire", "vraie distance metrique", "TSP metrique")
        d.space(0.01)
        formula(d, r"$D[i][k] \;\leq\; D[i][j] + D[j][k]$", size=14, height=0.05)
        d.body("Cette derniere propriete (inegalite triangulaire) fait de l'instance un "
               "TSP METRIQUE : elle valide le 2-opt et donne au plus proche voisin sa "
               "garantie de qualite theorique.")

        # ---- 7 ----
        d.h1("7. La symetrisation explicite")
        d.body("En mode osm, la matrice REELLE est asymetrique (sens uniques : "
               "t(u,v) != t(v,u)). Pour que le 2-opt reste valide (inverser un segment ne "
               "doit pas changer son cout), symmetrize() moyenne les deux sens :")
        formula(d, r"$D[i][j] \;\leftarrow\; \frac{D[i][j] + D[j][i]}{2}$",
                size=15, height=0.055)
        d.body("En mode hypothese la matrice est DEJA symetrique : cette operation ne "
               "change rien, mais elle est appliquee par coherence. Elle reste une "
               "hypothese de modelisation a assumer, pas un detail technique.")

        # ---- 8 ----
        d.h1("8. Deux unites, un seul graphe")
        d.body("La matrice en SECONDES (step1) et la matrice en METRES (step4) decrivent "
               "le MEME graphe a un facteur d'echelle pres :")
        formula(d, r"$t = d \,/\, 8{,}333$", size=14, height=0.05)
        d.body("C'est pourquoi le classement des algorithmes est identique dans les deux "
               "unites : changer d'unite ne change pas quel tour est le plus court.")

        # ---- 9 ----
        d.h1("9. Synthese des choix methodologiques (a defendre)")
        d.bullet("Convention [lon, lat] + depot = point 0 : structuration des donnees.")
        d.bullet("Graphe complet : chaque trajet reel resume par un poids unique (903 aretes).")
        d.bullet("Haversine plutot qu'euclidien plat : respecte la courbure et le "
                 "resserrement des meridiens ; verifie equivalent au plan local au quartier.")
        d.bullet("Poids = temps, pas distance : fidelite au probleme de collecte (t = d / v).")
        d.bullet("AVG_SPEED = 30 km/h constante : hypothese forte (ni type de voie, ni "
                 "trafic) coherente avec la collecte 5h-7h a Meknes.")
        d.bullet("DETOUR_FACTOR = 1,0 : borne 'vol d'oiseau pur', reglable pour relacher "
                 "l'hypothese.")
        d.bullet("Symetrisation : rend le graphe non oriente pour legitimer le 2-opt.")
        d.bullet("Deux unites, un seul graphe : metres (lisibilite) et secondes "
                 "(resolution), reliees par un facteur d'echelle.")
        d.body("Le tout produit une matrice 43 x 43, symetrique, a diagonale nulle, "
               "metrique : l'objet mathematique propre sur lequel tournent les trois "
               "algorithmes.")

        d.finish()

        # figures d'illustration en fin d'annexe
        insert_image(d, pdf, "graph_view.png",
                     "Illustration — le graphe pondere obtenu",
                     "Chaque sommet a sa position GPS reelle ; chaque arete porte la "
                     "distance (issue de haversine). Le carre est le depot (point 0).")
        insert_image(d, pdf, "adjacency_heatmap.png",
                     "Illustration — la matrice d'adjacence complete (43 x 43)",
                     "La meme information sous forme de tableau de couleurs : sombre = "
                     "proche, clair = lointain ; diagonale nulle, matrice symetrique.")

    print("PDF ecrit -> annexe_matrice_adjacence.pdf")


if __name__ == "__main__":
    main()
