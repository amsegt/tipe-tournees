# RAPPORT_OSM — Contre-epreuve sur le reseau routier reel (OSM)

> Genere par `compare_hypo_osm.py`. **Tous les chiffres proviennent d'executions reelles** (mode OSM execute le 2026-06-07 via OSMnx 2.1.0 sur les memes 43 points). Aucun nombre n'a ete invente ; le mode hypothese n'a pas ete modifie.

## Reseau telecharge (reproductible)

- Reseau OSM `drive` : **2542 noeuds, 7257 aretes** (rayon 1421 m ; 13 noeuds hors composante fortement connexe retires pour garantir la routabilite).
- Cache : `road_graph.graphml`. Vitesses par type de voie : {'residential': 30, 'living_street': 20, 'tertiary': 40, 'secondary': 50, 'primary': 60, 'trunk': 70} (fallback 30 km/h).
- Paires non connectees : **0**.

## 1. Temps de tournee OSM (43 points) + ecart vs hypothese

| Methode | Hypothese | OSM | Ratio OSM/Hypo |
|---|---|---|---|
| Plus proche voisin (depart 0) | 18 min 12 s | 17 min 20 s | x0.952 |
| Plus proche voisin (meilleur depart) | 16 min 26 s | 16 min 05 s | x0.978 |
| 2-opt (sur meilleur PPV) | 13 min 23 s | 14 min 43 s | x1.100 |

> Les temps OSM sont calcules sur la matrice **symetrisee** (comme en hypothese, pour comparer a modele egal). A titre indicatif, le cout **reel oriente** (matrice asymetrique) du meilleur cycle 2-opt vaut 15 min 17 s.

## 2. Le classement change-t-il ? L'ordre de visite change-t-il ?

- **Classement des methodes** — hypothese : 2-opt (sur meilleur PPV) < Plus proche voisin (meilleur depart) < Plus proche voisin (depart 0).
- **Classement des methodes** — OSM : 2-opt (sur meilleur PPV) < Plus proche voisin (meilleur depart) < Plus proche voisin (depart 0).
- **Le classement est INCHANGE** : le 2-opt reste le meilleur, devant le PPV meilleur depart, devant le PPV depart depot.
- **Ordre de visite du meilleur cycle (2-opt)** : DIFFERENT entre hypothese et OSM.
- Par methode, meme ordre de visite hypo vs OSM :
  - Plus proche voisin (depart 0) : non
  - Plus proche voisin (meilleur depart) : non
  - 2-opt (sur meilleur PPV) : non

> Interpretation : que l'ordre de visite **change** est **attendu et sain** — les vrais temps routiers (sens uniques, types de voie) reordonnent localement le tour. Ce qui compte pour le message du TIPE, c'est que le **classement des algorithmes ne change pas**.

## 3. Etalonnage OSM (7 sous-quartiers x 14 points) — le +0,9 % tient-il ?

| Heuristique | Ecart moyen hypo | Ecart moyen OSM | max OSM |
|---|---|---|---|
| PPV (depot) | +14.4 % | +6.4 % | +9.2 % |
| PPV (meilleur depart) | +11.1 % | +4.2 % | +9.2 % |
| **2-opt** | **+0.9 %** | **+1.6 %** | +4.2 % |

- Optimum exact atteint par 2-opt : **2/7** en hypothese, **3/7** en OSM.
- **Verdict** : le 2-opt reste **quasi-optimal en OSM** (+1.6 % en moyenne). Le chiffre exact **+0,9 % ne tient pas tel quel** (il devient +1.6 %), mais l'ordre de grandeur (~1-2 %, tres en dessous du PPV) est **confirme**.
- A noter : en OSM, le PPV est **plus proche** de l'optimum qu'en hypothese (+6.4 % vs +14.4 %), probablement parce que le reseau reel contraint les trajets.

## 4. Erreur de snapping (rattachement point -> noeud)

- **max = 89.5 m**, **moyenne = 15.1 m** (detail par point dans `snapping_osm.csv`).
- Impact credible : a 30 km/h, 90 m representent ~11 s sur le pire point ; l'erreur moyenne est negligeable devant des trajets de plus d'une minute. Le snapping n'altere pas les conclusions.

## 5. La carte reelle est-elle exploitable (objectif 4 MCOT) ?

- **Oui.** `best_tour_osm.png` trace le meilleur cycle 2-opt **le long des rues reelles** (fond OpenStreetMap), et `best_tour_osm.html` est une carte **interactive** (folium) zoomable avec marqueurs des conteneurs et du depot.
- C'est la visualisation cartographique demandee, qui remplace le schema noeuds-liens du mode hypothese.

## Conclusion

Le mode OSM **renforce** le message du TIPE sans le contredire : le classement des algorithmes est stable, le 2-opt reste quasi-optimal (+1.6 % vs l'exact), et on dispose desormais d'une vraie carte. La seule nuance honnete : la valeur precise de l'ecart 2-opt depend du modele de temps (+0,9 % en hypothese, +1.6 % en OSM) — ce qui **valide la robustesse de l'approche** tout en montrant que l'hypothese de vitesse constante etait optimiste sur la qualite absolue des heuristiques simples.

*Fichiers : results_osm.csv, calibration_results_osm.csv, travel_time_matrix_osm(.|_sym).csv, road_graph.graphml, snapping_osm.csv, osm_build_stats.json, best_tour_osm.png/.html, compare_hypo_osm.csv.*
