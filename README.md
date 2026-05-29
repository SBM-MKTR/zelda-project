# Adventure

Un jeu d'aventure top-down en 2D, inspiré de The Legend of Zelda. Tu explores une carte, tu collectes des cristaux, tu évites des ennemis, et tu résous de petits puzzles pour ouvrir des portails. Le but est de récolter tous les cristaux.

## Lancer le jeu

```bash
uv run main.py
```

Il faut taper cette commande dans le terminal. Le jeu s'ouvre avec la carte par défaut.

On peut aussi charger une carte différente en passant son chemin en argument :

```bash
uv run main.py Maps/ma_carte.txt
```

## Contrôles

| Touche | Action |
|--------|--------|
| ↑ ↓ ← → | Déplacer le joueur |
| D | Utiliser l'arme active |
| R | Changer d'arme (boomerang ou épée) |
| Échap | Abandonner la partie |
| Enter | Relancer la partie lorsqu'on est sur l'écran de fin

## Ce qu'il y a dans le jeu

**Les ennemis** : trois types, chacun avec son comportement. Les spinners font des allers-retours en ligne droite et ne se soucient pas de toi. Les chauves-souris volent de manière aléatoire dans leur zone. Les blobs, eux, te repèrent s'ils ont une ligne de vue sur toi, et viennent te chercher en contournant les obstacles. Le joueur meurt au contact des ennemis.

**Les armes** : le boomerang part dans la direction où tu regardes, tue les ennemis sur son passage, et revient automatiquement vers toi. L'épée est une attaque au corps-à-corps instantanée. Les deux peuvent activer les interrupteurs, seule l'épée peut ramasser les cristaux.

**Les interrupteurs et les portails** : certains passages sont bloqués par des portails. Pour les ouvrir, il faut activer les bons interrupteurs en les touchant avec une arme. Les conditions peuvent être complexes : un portail peut nécessiter que plusieurs interrupteurs soient activés en même temps, ou qu'un seul le soit.

**Les téléporteurs** : marches sur un téléporteur et tu te retrouves directement ailleurs sur la carte.

**Les clés et les coffres** : certains coffres sont verrouillés. Trouve la clé correspondante sur la carte, puis approche-toi du coffre pour l'ouvrir. À l'intérieur : un pouvoir aléatoire. Le pouvoir Ghost te rend invincible et semi-transparent pendant quelques secondes. Le pouvoir Freeze fige tous les ennemis sur place.

**La glace** : certaines zones sont recouvertes de glace.

**Les trous** : si tu t'approches trop près du centre d'un trou, tu tombes et tu meurs instantanément.

## Créer sa propre carte

Les cartes sont des fichiers texte simples dans le dossier `Maps/`. Voici un exemple :

```
width: 14
height: 10
switches:
- id: sw1
  x: 2
  y: 7
  state: off
- id: sw2
  x: 11
  y: 7
  state: off
gates:
- x: 7
  y: 5
  open_if:
    and:
      - switch_is_on: sw1
      - switch_is_on: sw2
teleporters:
- id: tp1
  x: 2
  y: 2
  target_id: tp2
- id: tp2
  x: 11
  y: 2
  target_id: tp1
keys:
- id: key1
  x: 5
  y: 7
chests:
- id: chest1
  x: 9
  y: 7
  key_id: key1
---
xxxxxxxxxxxxxx
x            x
x ^  k   C ^ x
x            x
x      |     x
x     * *    x
x            x
x T        T x
x     P      x
xxxxxxxxxxxxxx
---
```
Dans cet exemple : le joueur démarre en bas au centre. La porte (`|`) au milieu de la carte bloque l'accès aux cristaux du haut. Pour l'ouvrir, il faut activer les deux interrupteurs (`^`) en haut avec une arme. La clé (`k`) permet d'ouvrir le coffre (`C`) voisin pour obtenir un pouvoir. Les deux téléporteurs (`T`) en bas permettent de passer d'un côté à l'autre de la carte instantanément.

Chaque caractère représente une case :

| Caractère | Signification |
|-----------|---------------|
| `x` | Buisson (mur) |
| ` ` | Herbe |
| `*` | Cristal à collecter |
| `P` | Position de départ du joueur (obligatoire, un seul) |
| `s` / `S` | Spinner horizontal / vertical |
| `v` | Chauve-souris |
| `b` | Blob |
| `O` | Trou |
| `g` | Glace |
| `T` | Téléporteur |
| `k` | Clé |
| `C` | Coffre |
| `^` | Interrupteur |
| `\|` | Portail |

Il suffit donc de mettre le caractère souhaité où l'on veut, en pensant à mettre les configurations des portails, interrupteurs, téléporteurs, clés et coffres en haut du fichier, dans le bon format.
