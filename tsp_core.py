# -*- coding: utf-8 -*-
"""
tsp_core.py — Les trois algorithmes du TIPE + utilitaires.

Contient :
  - tour_length        : longueur d'un tour
  - nearest_neighbor   : plus proche voisin (glouton)
  - nearest_neighbor_best_start
  - two_opt            : amelioration locale 2-opt
  - held_karp          : resolution exacte (programmation dynamique)
  - brute_force        : reference exacte (verification de Held-Karp)
  - read_matrix_csv / symmetrize : utilitaires sur la matrice de couts

Ce module est importe par step2_solve.py. Il ne fait AUCUN acces reseau.
"""
from itertools import permutations
import csv
import math


# --------------------------------------------------------------------------
# Utilitaires sur la matrice
# --------------------------------------------------------------------------
def read_matrix_csv(path):
    """Lit une matrice carree depuis un CSV (valeurs separees par des virgules)."""
    D = []
    with open(path, newline="") as f:
        for row in csv.reader(f):
            if row:
                D.append([float(x) for x in row])
    n = len(D)
    for r in D:
        assert len(r) == n, "La matrice doit etre carree."
    return D


def symmetrize(D):
    """Rend la matrice symetrique : T[i][j] <- (T[i][j] + T[j][i]) / 2.

    A utiliser si la matrice routiere est asymetrique (sens uniques).
    C'est une hypothese de modelisation a assumer devant le jury.
    """
    n = len(D)
    return [[(D[i][j] + D[j][i]) / 2.0 for j in range(n)] for i in range(n)]


def tour_length(tour, D):
    """Longueur totale du cycle (retour au depart inclus)."""
    n = len(tour)
    return sum(D[tour[i]][tour[(i + 1) % n]] for i in range(n))


# --------------------------------------------------------------------------
# 1. PLUS PROCHE VOISIN
# --------------------------------------------------------------------------
def nearest_neighbor(D, start=0):
    """Construit un tour par la regle du plus proche voisin. Cout O(n^2)."""
    n = len(D)
    tour = [start]
    visited = [False] * n
    visited[start] = True
    current = start
    for _ in range(n - 1):
        best_dist, best_j = math.inf, -1
        for j in range(n):
            if not visited[j] and D[current][j] < best_dist:
                best_dist, best_j = D[current][j], j
        tour.append(best_j)
        visited[best_j] = True
        current = best_j
    return tour


def nearest_neighbor_best_start(D):
    """Lance le PPV depuis chaque sommet et garde le meilleur tour. Cout O(n^3)."""
    best_tour, best_len = None, math.inf
    for s in range(len(D)):
        t = nearest_neighbor(D, s)
        L = tour_length(t, D)
        if L < best_len:
            best_len, best_tour = L, t
    return best_tour


# --------------------------------------------------------------------------
# 2. DEUX-OPT (suppose une matrice symetrique)
# --------------------------------------------------------------------------
def two_opt(tour, D):
    """Ameliore un tour par 2-opt jusqu'a l'optimum local. O(n^2) par passe."""
    tour = tour[:]                       # on ne modifie pas l'entree
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = tour[i - 1], tour[i]
                c, d = tour[j], tour[(j + 1) % n]
                if d == a:
                    continue
                delta = (D[a][c] + D[b][d]) - (D[a][b] + D[c][d])
                if delta < -1e-9:
                    tour[i:j + 1] = tour[i:j + 1][::-1]
                    improved = True
    return tour


# --------------------------------------------------------------------------
# 3. HELD-KARP (exact, programmation dynamique)
# --------------------------------------------------------------------------
def _subsets(elems, k):
    elems = list(elems)
    if k == 0:
        yield ()
        return
    if k > len(elems):
        return
    for i in range(len(elems)):
        for rest in _subsets(elems[i + 1:], k - 1):
            yield (elems[i],) + rest


def held_karp(D):
    """Resolution EXACTE du TSP. Temps O(n^2 * 2^n), memoire O(n * 2^n).

    Renvoie (tour, cout). A reserver aux petites instances (n <= ~15).
    """
    n = len(D)
    C = {}
    for j in range(1, n):
        C[(1 << j, j)] = (D[0][j], 0)
    for size in range(2, n):
        for subset in _subsets(range(1, n), size):
            bits = 0
            for k in subset:
                bits |= 1 << k
            for j in subset:
                prev = bits & ~(1 << j)
                C[(bits, j)] = min((C[(prev, i)][0] + D[i][j], i)
                                   for i in subset if i != j)
    full = (1 << n) - 2
    cost, parent = min((C[(full, j)][0] + D[j][0], j) for j in range(1, n))
    tour, bits, j = [0], full, parent
    for _ in range(n - 1):
        tour.append(j)
        bits, j = bits & ~(1 << j), C[(bits, j)][1]
    return tour[::-1], cost


# --------------------------------------------------------------------------
# 4. FORCE BRUTE (reference de verification)
# --------------------------------------------------------------------------
def brute_force(D):
    """Enumere les (n-1)! tours. A reserver a n <= ~10 (verification)."""
    n = len(D)
    best_len, best = math.inf, None
    for perm in permutations(range(1, n)):
        t = [0] + list(perm)
        L = tour_length(t, D)
        if L < best_len:
            best_len, best = L, t
    return best, best_len
