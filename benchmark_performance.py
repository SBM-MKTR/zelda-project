"""Benchmark de performance du jeu.

Génère programmatiquement des cartes en faisant varier deux facteurs sur
plusieurs ordres de grandeur, mesure les deux fonctions critiques et produit
deux graphes (matplotlib) :

1. Chargement d'une map  -> facteur : taille de la carte m = width x height.
2. GameView.on_update    -> facteur : nombre de blobs k (carte fixe).

Les graphes sont enregistrés dans le dossier ``benchmarks/`` et les mesures
brutes sont affichées sur la sortie standard.

Usage :
    uv run benchmark_performance.py
"""

import statistics
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend headless : aucun affichage requis
import matplotlib.pyplot as plt

import arcade

from constants import BLOB_NAVMESH_SUBDIVISIONS
from level import build_level
from gameview import GameView
from map import Map
from navmesh import build_navmesh


OUTPUT_DIR = Path("benchmarks")

# Tailles de carte (côté) pour le chargement : m = side^2 couvre ~3 ordres
# de grandeur (25 -> ~12000 cellules).
LOAD_SIDES = [5, 8, 12, 18, 26, 38, 55, 80, 110]

# Nombres de blobs pour on_update (carte fixe), couvrant ~3 ordres de grandeur.
UPDATE_BLOB_COUNTS = [1, 3, 5, 10, 50, 100, 500, 1000]
UPDATE_MAP_SIDE = 34  # 32x32 = 1024 cellules intérieures -> tient 1000 blobs


def make_open_map(width: int, height: int) -> str:
    """Carte rectangulaire entièrement ouverte (bordure de buissons)."""
    rows: list[str] = []
    for y in range(height):
        if y == 0 or y == height - 1:
            rows.append("x" * width)
        else:
            rows.append("x" + " " * (width - 2) + "x")

    player_row = list(rows[height - 2])
    player_row[1] = "P"
    rows[height - 2] = "".join(player_row)

    return f"width: {width}\nheight: {height}\n---\n" + "\n".join(rows) + "\n---\n"


def make_blob_map(side: int, blob_count: int) -> str:
    """Carte carrée ouverte avec ``blob_count`` blobs placés dans l'intérieur."""
    grid = [["x" if (x in (0, side - 1) or y in (0, side - 1)) else " "
             for x in range(side)]
            for y in range(side)]

    free_cells = [
        (x, y)
        for y in range(1, side - 1)
        for x in range(1, side - 1)
    ]

    px, py = free_cells[0]
    grid[py][px] = "P"

    placed = 0
    for (x, y) in free_cells[1:]:
        if placed >= blob_count:
            break
        grid[y][x] = "b"
        placed += 1

    if placed < blob_count:
        raise ValueError("carte trop petite pour le nombre de blobs demandé")

    rows = ["".join(row) for row in grid]
    return f"width: {side}\nheight: {side}\n---\n" + "\n".join(rows) + "\n---\n"


def time_call(call: Callable[[], object], repeats: int) -> float:
    """Renvoie le temps médian (en secondes) d'un appel répété ``repeats`` fois."""
    timings: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        call()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings)


def benchmark_load() -> list[tuple[int, int, float]]:
    """Mesure le temps de chargement complet (parsing + build_level + navmesh).

    Renvoie une liste de (m, V, temps_secondes).
    """
    results: list[tuple[int, int, float]] = []

    for side in LOAD_SIDES:
        text = make_open_map(side, side)
        m = side * side

        def load() -> None:
            game_map = Map.from_string(text)
            build_level(game_map)

        load()  # warmup (atlas de textures, etc.)
        elapsed = time_call(load, repeats=5)

        # Nombre de noeuds du navmesh (pour information dans le tableau).
        v = len(build_navmesh(Map.from_string(text), BLOB_NAVMESH_SUBDIVISIONS).nodes)

        results.append((m, v, elapsed))
        print(f"  chargement  m={m:>6}  V={v:>7}  {elapsed * 1000:>9.3f} ms")

    return results


def benchmark_update(window: arcade.Window) -> list[tuple[int, float]]:
    """Mesure le temps moyen d'un appel à on_update en fonction du nombre de blobs.

    Renvoie une liste de (k, temps_secondes).
    """
    results: list[tuple[int, float]] = []
    warmup_frames = 10
    timed_frames = 60

    for k in UPDATE_BLOB_COUNTS:
        text = make_blob_map(UPDATE_MAP_SIDE, k)
        game_map = Map.from_string(text)
        view = GameView(game_map)
        window.show_view(view)

        # On neutralise le redémarrage : si le joueur (immobile) est touché par
        # un blob, on ne veut pas recréer une vue pendant la mesure.
        view._restart = lambda won=False: None  # type: ignore[method-assign]

        for _ in range(warmup_frames):
            view.on_update(1 / 60)

        timings: list[float] = []
        for _ in range(timed_frames):
            start = time.perf_counter()
            view.on_update(1 / 60)
            timings.append(time.perf_counter() - start)

        mean = statistics.mean(timings)
        results.append((k, mean))
        print(f"  on_update   k={k:>4}  {mean * 1000:>9.4f} ms/frame")

    return results


def _fit_through_origin(xs: list[float], ys: list[float]) -> float:
    """Pente c de la droite y = c*x au sens des moindres carrés."""
    num = sum(x * y for x, y in zip(xs, ys))
    den = sum(x * x for x in xs)
    return num / den


def plot_load(results: list[tuple[int, int, float]]) -> Path:
    ms = [m for m, _v, _t in results]
    times_ms = [t * 1000 for _m, _v, t in results]

    slope = _fit_through_origin(ms, times_ms)
    ref = [slope * m for m in ms]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ms, times_ms, "o-", color="#1f77b4", label="Mesuré")
    ax.plot(ms, ref, "--", color="#888888", label="Référence O(m) (linéaire)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Taille de la carte m = width × height (cellules)")
    ax.set_ylabel("Temps de chargement (ms)")
    ax.set_title("Chargement d'une map : temps vs taille de carte\n"
                 f"(navmesh à n = {BLOB_NAVMESH_SUBDIVISIONS} subdivisions)")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()

    path = OUTPUT_DIR / "chargement.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_update(results: list[tuple[int, float]]) -> Path:
    ks = [k for k, _t in results]
    times_ms = [t * 1000 for _k, t in results]

    slope = _fit_through_origin(ks, times_ms)
    ref = [slope * k for k in ks]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ks, times_ms, "o-", color="#9467bd", label="Mesuré")
    ax.plot(ks, ref, "--", color="#888888", label="Référence O(k) (linéaire)")
    ax.axhline(1000 / 60, color="#d62728", ls="-.", alpha=0.7,
               label="Budget 60 FPS (16.67 ms)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Nombre de blobs k (carte fixe)")
    ax.set_ylabel("Temps moyen par on_update (ms)")
    ax.set_title("on_update : temps vs nombre de blobs")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend()
    fig.tight_layout()

    path = OUTPUT_DIR / "on_update.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    window = arcade.Window(640, 480, "Benchmark", visible=False)

    print("== Chargement (facteur : taille de carte m) ==")
    load_results = benchmark_load()

    print("\n== on_update (facteur : nombre de blobs k) ==")
    update_results = benchmark_update(window)

    window.close()

    load_path = plot_load(load_results)
    update_path = plot_update(update_results)

    print(f"\nGraphes écrits :\n  {load_path}\n  {update_path}")


if __name__ == "__main__":
    main()
