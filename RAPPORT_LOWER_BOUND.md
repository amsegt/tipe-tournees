# RAPPORT_LOWER_BOUND — Minorant certifie de l'optimum (43 points)

> Genere par `step6_lower_bound.py`. **Tous les chiffres proviennent d'une execution reelle**, deterministe (aucun alea). On ne calcule PAS l'optimum exact (infaisable a n=43) : on l'ENCADRE.

## Principe

Pour tout minorant `LB` de l'optimum : `LB <= OPT <= cout_2opt`. Donc l'**ecart certifie** `(cout_2opt - LB)/LB` **majore** l'ecart reel du 2-opt a l'optimum. Plus le minorant est haut, plus la garantie est fine.

## Resultats

| Mode | MST | 1-arbre | Held-Karp LB | Cout 2-opt (UB) | Ecart certifie (MST) | (1-arbre) | **(Held-Karp)** |
|---|---|---|---|---|---|---|---|
| Hypothese | 612 s | 645 s | 762 s | 803 s | +31.1 % | +24.5 % | **+5.3 %** |
| OSM | 670 s | 703 s | 840 s | 883 s | +31.9 % | +25.7 % | **+5.2 %** |

Le minorant de Held-Karp (relaxation lagrangienne du 1-arbre, 2000 iterations, pas de Polyak) est le plus serre des trois (MST <= 1-arbre <= Held-Karp <= OPT). Voir la montee du minorant dans `lower_bound_convergence.png`.

## Verdict

**Sur l'instance reelle de 43 points, le 2-opt est PROUVE a moins de 5.3 % de l'optimum, sans extrapolation** (hypothese : +5.3 % ; OSM : +5.2 %).

Ce minorant **complete** (ne remplace pas) l'etalonnage Held-Karp exact sur 14 points : l'etalonnage montre ~1 % d'ecart MOYEN en pratique, le minorant donne une GARANTIE pire-cas sur l'instance complete de 43 points. Message consolide : *2-opt prouve sous ~5 % sur 43 points, et ~1 % en pratique d'apres l'etalonnage.*

*Fichiers : lower_bound_results.csv, lower_bound_convergence.png.*
