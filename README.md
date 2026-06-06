# TIPE 13530 — Tournées de collecte : guide de lancement

Pipeline complet pour passer de **tes points (GeoJSON)** à la **comparaison des trois
algorithmes** (plus proche voisin, 2-opt, Held-Karp) d'un quartier de Meknès, avec
visualisation du meilleur cycle.

`step1` propose **deux méthodes** pour les poids (temps de trajet) :
- **`"hypothesis"`** (par défaut) — *hypothèse forte* : distance à vol d'oiseau parcourue à
  vitesse moyenne constante. Aucune dépendance lourde, aucun accès réseau, instantané.
- **`"osm"`** — réseau routier réel via OSMnx (plus fidèle, nécessite Internet + `osmnx` +
  `scikit-learn`).

Utiliser les deux et comparer leurs résultats est un excellent argument méthodologique.

```
points.geojson  ──step1──▶  travel_time_matrix.csv  ──step2──▶  results.csv + best_tour.json
                            coords.csv                                        │
                            road_graph.graphml ─────────────step3────────────▶ best_tour.png
```

---

## 1. Prérequis (une seule fois)

- **Python 3.10 ou plus** — vérifie avec `python --version` (ou `python3 --version`).
  Si absent : installe-le depuis python.org en **cochant « Add Python to PATH »**.
- **VSCode** + l'extension **Python** (éditeur → onglet Extensions → cherche « Python » de Microsoft).

## 2. Ouvrir le projet dans VSCode

1. Dézippe le dossier `tipe_tournees` quelque part (ex. `Documents`).
2. Dans VSCode : `Fichier → Ouvrir le dossier…` → choisis `tipe_tournees`.
3. Ouvre un terminal intégré : `Terminal → Nouveau terminal` (ou `Ctrl+ô`).

## 3. Créer un environnement isolé et installer les dépendances

Un *environnement virtuel* évite de polluer ton Python système. Dans le terminal VSCode :

**Windows :**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux :**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> VSCode te proposera peut-être « *Nous avons remarqué un nouvel environnement, le sélectionner ?* » → **Oui**.
> Sinon : `Ctrl+Shift+P` → « Python: Select Interpreter » → choisis celui dans `.venv`.

> **Léger par défaut.** En mode `"hypothesis"`, seul `matplotlib` est utilisé : si tu n'utilises
> pas le mode `"osm"`, tu peux te contenter de `pip install matplotlib` et ignorer la suite.

L'installation d'OSMnx (utile **uniquement** pour le mode `"osm"`) tire automatiquement
`geopandas`, `shapely`, etc.
**Si `pip` échoue sous Windows** (compilation de dépendances géographiques), installe plutôt
via conda/mamba :
```bash
conda create -n tipe python=3.12 osmnx networkx matplotlib -c conda-forge
conda activate tipe
```

## 4. Déposer tes points

Place ton fichier exporté de geojson.io dans le dossier et nomme-le **`points.geojson`**.
Le format attendu (voir `points.geojson.example`) : des entités `Point` avec
`"coordinates": [longitude, latitude]`. **Le premier point du fichier est le dépôt**
(point de départ et d'arrivée du cycle).

## 5. Lancer les trois étapes

Toujours dans le terminal (environnement activé) :

```bash
python step1_build_matrix.py    # télécharge le réseau OSM + construit la matrice des temps
python step2_solve.py           # lance PPV, 2-opt, Held-Karp et compare
python step3_plot_map.py        # dessine le meilleur cycle -> best_tour.png
```

(Tu peux aussi cliquer le triangle ▶ « Run » en haut à droite de chaque fichier ouvert.)

**Ce que tu obtiens :**

| Fichier | Contenu |
|---|---|
| `travel_time_matrix.csv` | matrice n×n des temps de trajet (secondes) |
| `coords.csv` | coordonnées de tes points, dans l'ordre |
| `road_graph.graphml` | le réseau routier (pour la carte) |
| `results.csv` | tableau comparatif des trois méthodes |
| `best_tour.json` | le meilleur tour trouvé |
| `best_tour.png` | la carte du cycle |

`step2` affiche directement dans le terminal le temps de chaque cycle, le temps de calcul,
et **l'écart en % à l'optimum exact** (quand Held-Karp tourne).

---

## 6. Les paramètres à régler (et à défendre devant le jury)

Ouvre les fichiers et ajuste les blocs « PARAMÈTRES » en haut :

- **`METHOD`** (dans `step1`) — `"hypothesis"` (défaut) ou `"osm"`.
- **`AVG_SPEED_KMH`** (mode hypothèse) — la **vitesse moyenne constante** supposée. C'est
  *l'hypothèse forte* : on admet que le camion roule partout à cette vitesse. Choisis une
  valeur réaliste pour une collecte en ville (≈ 20-30 km/h) et justifie-la.
- **`DETOUR_FACTOR`** (mode hypothèse) — `1.0` = distance à vol d'oiseau pure (hypothèse la
  plus forte). Le passer à ≈ `1.3` *relâche* l'hypothèse en approchant grossièrement les
  détours routiers (un trajet réel est ~30 % plus long que la ligne droite).
- **`HWY_SPEEDS`** (mode `osm`) — les vitesses (km/h) par type de voie. Les valeurs par
  défaut sont génériques : **remplace-les par des estimations réalistes pour Meknès** et sois
  prêt à les justifier. C'est le cœur de ta formule MCOT `t = d / v(type_voie)`.
- **`SYMMETRIZE`** (dans `step2`, `True` par défaut) — la matrice routière est *asymétrique*
  (sens uniques : `t(u,v) ≠ t(v,u)`). On la rend symétrique en moyennant les deux sens pour
  que 2-opt reste valide. **C'est une hypothèse de modélisation à assumer**, pas un détail
  technique. Mets `False` pour observer l'asymétrie brute (mais alors 2-opt n'est plus
  rigoureusement justifié).
- **`HELD_KARP_MAX`** (dans `step2`, 15) — au-delà, Held-Karp sature la mémoire et est sauté.
  Pour l'utiliser comme **étalon**, lance le pipeline sur un sous-ensemble de ≤ 15 points.
- **`BUFFER_M`** (dans `step1`) — marge autour de tes points pour télécharger le réseau.

## 7. Étalonner les heuristiques (la manip qui impressionne le jury)

Held-Karp ne tourne pas sur 30-40 points. Pour mesurer la qualité de PPV/2-opt :
1. fais un `points.geojson` réduit à ~12-15 points,
2. lance les trois étapes : `step2` affiche alors l'écart exact en % à l'optimum,
3. répète sur plusieurs sous-quartiers → tu obtiens une **distribution d'écarts** à montrer.

## 8. Dépannage

- **« No data elements / place not found »** : on télécharge par centre + rayon, pas par nom,
  donc ça doit marcher ; si le réseau est vide, augmente `BUFFER_M` ou vérifie tes coordonnées
  (ordre `[lon, lat]`, pas l'inverse).
- **`results.csv` montre des temps `inf`** : ton réseau est morcelé (deux zones non reliées
  par une route conduisible). Vérifie tes points, augmente `BUFFER_M`.
- **`step3` retombe sur le « schéma »** : `road_graph.graphml` est absent (relance `step1`) ;
  le schéma reste correct, il montre l'ordre de visite (segments droits, non les rues).
- **Held-Karp très lent / mémoire** : baisse le nombre de points ou `HELD_KARP_MAX`.

## 9. Rappels de rigueur (pour la soutenance)

- Les **temps sont des estimations** (vitesses libres, sans trafic) cohérentes avec ton
  hypothèse « collecte 5h-7h » — dis-le, ne le cache pas.
- Le **snapping** (rattachement des points aux routes) introduit une petite erreur : `step1`
  affiche la distance max ; mentionne-la.
- Tu résous un **TSP** ; le vrai problème de collecte est un **CARP/VRP**. Simplification
  assumée (voir ton annexe de compréhension).
- En mode `"hypothesis"`, tes temps reposent sur une **hypothèse forte** (vol d'oiseau,
  vitesse constante) : annonce-la clairement comme une **borne / première approximation**.
  L'idéal pour le jury : produire la matrice dans les **deux** modes et montrer si le
  classement des algorithmes change ou non — c'est une vraie analyse de robustesse.
