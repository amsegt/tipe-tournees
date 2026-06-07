# Instructions IA — TIPE 13530 · Contre-épreuve OSM (réseau routier réel)

> **À lire intégralement avant d'écrire la moindre ligne de code.**
> Ce fichier garde l'IA qui code (Claude dans VS Code) alignée avec les livrables déjà produits
> (deck 20 slides, script oral, annexe maître) et avec les chiffres vérifiés du dépôt.
> Objectif unique de cette tâche : exécuter pour de vrai le **mode OSM**, qui n'a jamais tourné.

---

## 1. Contexte (ne pas dévier)

- **Candidat** : Brahim AMSEGT, n° 13530, CPGE **MP**, session 2026, **monôme**.
- **Titre** : *Optimisation des tournées de collecte des déchets urbains*.
- **Thème** : « Cycles, boucles ».
- **Problème** : TSP (cycle hamiltonien de poids minimal) sur un quartier de Meknès modélisé en graphe pondéré par le **temps de trajet**.
- **Dépôt** : `github.com/amsegt/tipe-tournees`. Scripts : `step1_build_matrix.py`, `step2_solve.py`, `step3_plot_map.py` (ou équivalent), `step5_calibrate.py`, `tsp_core.py`.
- **Trois algorithmes** : plus proche voisin (PPV, O(n²)), 2-opt (recherche locale), Held-Karp (exact, O(n²·2ⁿ), uniquement n ≤ 15 ; sert d'étalon). La « force brute » historique (O((n−1)!)) ne sert que de **vérificateur** sur petites instances.

## 2. Vérité-terrain VERROUILLÉE (ne JAMAIS inventer ni « améliorer » ces chiffres)

Ces valeurs sont **déjà** dans le deck/script/annexe. Le code OSM ne doit pas les écraser : il **ajoute** un mode parallèle.

**Mode hypothèse (vol d'oiseau, vitesse constante 30 km/h, matrice symétrique par construction)** — instance complète à **43 points** (1 dépôt + 42 conteneurs) :

| Méthode | Temps de cycle | Temps de calcul |
|---|---|---|
| PPV (départ dépôt) | 1091,78 s = 18 min 12 s | ≈ 0,1 ms |
| PPV (meilleur départ) | 986,23 s = 16 min 26 s | ≈ 3,8 ms |
| 2-opt (sur meilleur PPV) | 802,60 s = 13 min 23 s | ≈ 1,0 ms |

- Gain 2-opt : **−26,5 %** vs PPV-dépôt, **−18,6 %** vs meilleur PPV.
- **Étalonnage** (7 sous-quartiers de **14 points**, Held-Karp = optimum exact) : écart moyen PPV-dépôt **+14,4 %** (max +24,8 %), PPV-best **+11,1 %**, **2-opt +0,9 %** (max +3,7 %), optimum exact atteint **2 fois sur 7** (Q4, Q6).
- Held-Karp **n=43** : ≈ 1,6·10¹⁶ opérations, mémoire ≈ 3,8·10¹⁴ → **infaisable** (c'est pourquoi on étalonne sur 14 points).

> Source de vérité : `results.csv` et `calibration_results.csv`. Si un nombre calculé diffère, **ne pas réécrire le doc** : signaler l'écart dans le rapport final (§6).

## 3. Décisions de modélisation à respecter (déjà défendues dans les docs)

- **TSP, pas CARP/VRP** : on collecte des **conteneurs discrets** (sommets), pas des rues. La **capacité du camion n'est pas une contrainte** car les bennes **compactent** les déchets (réduction de volume **~80–90 %**, *observation terrain à sourcer, ne pas présenter comme donnée constructeur*) → une tournée unique suffit.
- **Poids = temps** `t = d / v`. Mode hypothèse : `d` = haversine, `v` = 30 km/h constante (moyenne pondérée ≈ 0,4×50 + 0,6×20 ≈ 32 → 30).
- **Symétrisation** : en mode hypothèse, la matrice est **déjà symétrique** (no-op). La symétrisation ne sert **qu'en mode OSM**.
- **Robustesse (échelle)** : multiplier toute la matrice par un facteur ne change ni le tour optimal ni les écarts relatifs → le choix de la *valeur* de vitesse est sans impact comparatif. Cet argument **ne couvre pas** l'hypothèse de vitesse *constante* : c'est précisément ce que le mode OSM doit tester.

## 4. TÂCHE : exécuter le mode OSM (la contre-épreuve manquante)

Le mode OSM est **annoncé** dans les docs mais **jamais exécuté** (pas de `road_graph.graphml`, `results.csv` est 100 % hypothèse). Objectif : le faire tourner réellement, sur **les mêmes 43 points** (mêmes coordonnées `coords.csv` / `points.geojson`).

### 4.1 Étapes attendues
1. **Récupérer le réseau routier réel** autour des 43 points via **OSMnx** (graphe `drive`), le sauvegarder en `road_graph.graphml` (mise en cache, pour reproductibilité).
2. **Rattacher** chaque point de collecte au nœud routier le plus proche (`osmnx.distance.nearest_nodes`). Mesurer et **journaliser l'erreur de snapping** (distance point→nœud) max et moyenne.
3. **Matrice des temps OSM** : plus court chemin (Dijkstra, poids = temps de parcours par type de voie ; utiliser `travel_time` via `add_edge_speeds`/`add_edge_travel_times`, ou vitesses par `highway` documentées). Matrice **asymétrique** possible (sens uniques) → produire aussi une version **symétrisée** `(T+Tᵀ)/2` pour 2-opt, en gardant trace des deux.
4. **Rejouer les 3 algorithmes en mode OSM** : PPV (tous départs), 2-opt, et l'**étalonnage Held-Karp** sur les **mêmes 7 sous-quartiers de 14 points**. Réutiliser `tsp_core.py` tel quel (ne pas réécrire les algos).
5. **Vraie carte** (objectif 4 de la MCOT) : tracer le meilleur cycle 2-opt **sur le fond de carte OSM réel** (rues), pas un schéma nœuds-liens. Exporter en PNG haute résolution (`best_tour_osm.png`) + idéalement un HTML interactif (`folium`).
6. **Comparaison hypothèse vs OSM** : tableau récapitulatif (temps de tournée, écarts d'étalonnage, **est-ce que le classement des algorithmes change ? est-ce que l'ordre de visite change ?**). C'est le cœur de la contre-épreuve.

### 4.2 Sorties (fichiers) à produire
- `road_graph.graphml`
- `travel_time_matrix_osm.csv` (+ version symétrisée)
- `results_osm.csv` (même format que `results.csv`)
- `calibration_results_osm.csv` (même format que `calibration_results.csv`)
- `best_tour_osm.png` (carte réelle) et `best_tour_osm.html` (si folium)
- `compare_hypo_osm.csv` : par méthode, temps hypothèse vs OSM, et un booléen « même ordre de visite ».

## 5. Règles strictes (anti-régression, anti-hallucination)

- **Ne pas modifier** `results.csv`, `calibration_results.csv`, ni les scripts du mode hypothèse. Le mode OSM est **additif** (nouveaux fichiers suffixés `_osm`).
- **Ne réécris pas les algorithmes** (`tsp_core.py`) : seul le calcul de la **matrice** change.
- **Aucun chiffre inventé.** Tout nombre vient d'une exécution. Si OSMnx échoue (réseau, quota), **dis-le** et ne fabrique pas de résultats.
- **Reproductibilité** : fixer les versions (`requirements.txt`), mettre `road_graph.graphml` en cache, et journaliser tout (erreur de snapping, nb d'arêtes, etc.).
- **Environnement Windows** : pour `nearest_nodes` sur graphe non projeté, OSMnx exige scikit-learn → `pip install scikit-learn`. Documenter dans le README.
- **Honnêteté** : si le mode OSM **change** le classement ou les écarts, c'est un **résultat**, pas un échec — il faut le rapporter tel quel (cela validerait ou nuancerait l'hypothèse de vitesse constante).

## 6. Rapport final attendu (pour mettre à jour deck/script/annexe)

À la fin, produire un court `RAPPORT_OSM.md` répondant précisément à :
1. Temps de tournée OSM des 3 méthodes (43 points) + écart vs hypothèse.
2. Le **classement** PPV / 2-opt change-t-il en OSM ? L'**ordre de visite** du meilleur tour change-t-il ?
3. Écarts d'étalonnage OSM (7×14) vs hypothèse : le **+0,9 %** du 2-opt tient-il ?
4. Erreur de snapping (max, moyenne) — quel impact crédible ?
5. La **carte réelle** est-elle exploitable pour l'objectif 4 de la MCOT ?

Ces réponses me permettront de mettre à jour les trois livrables **sans inventer** : on y injectera les chiffres OSM réels et la vraie carte, et on transformera les mentions « le mode OSM fournirait une contre-épreuve » en résultats effectifs.

---

### Rappel cap
Le **message central** du TIPE ne doit pas bouger : *une heuristique simple (2-opt), bien **étalonnée** contre l'exact, donne une solution quasi-optimale pour un coût de calcul négligeable.* Le mode OSM sert à **renforcer** ce message (robustesse au modèle de temps + vraie cartographie), pas à le remplacer.