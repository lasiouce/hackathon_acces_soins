"""Criblage de Morris et indices de Sobol, en numpy (pas de SALib ni de scipy dans l'environnement).

Facteurs tirés dans [0, 1)^k ; le modèle traduit chaque coordonnée (continu ou discret).
  morris(model, k, r, rng)       r trajectoires à p = 4 niveaux, pas Δ = 2/3 ; EE = Y(x + Δe_i) − Y(x)
  sobol_design(k, n, rng)        matrices A, B et AB_i (Saltelli 2010)
  sobol_indices(yA, yB, yAB)     S1 (Saltelli 2010, sur Y centré) et ST (Jansen 1999)
  bootstrap(...)                 intervalle à 95 % par rééchantillonnage des lignes
"""
import numpy as np

P, DELTA = 4, 2 / 3


def morris_design(k: int, r: int, rng) -> list[tuple[np.ndarray, np.ndarray]]:
    """Chaque trajectoire : k + 1 points, un facteur bougé à la fois ; renvoie (points [k+1, k], ordre des facteurs)."""
    grid = np.arange(P) / (P - 1)
    out = []
    for _ in range(r):
        x = rng.choice(grid[grid + DELTA <= 1 + 1e-9], size=k)
        sign = rng.choice([-1, 1], size=k)
        x = np.where(sign < 0, x + DELTA, x)            # part d'en haut si on descend
        order = rng.permutation(k)
        pts = [x.copy()]
        for i in order:
            x = x.copy()
            x[i] += sign[i] * DELTA
            pts.append(x)
        out.append((np.clip(np.array(pts), 0, 1 - 1e-12), order))
    return out


def morris_effects(design, Y: np.ndarray) -> np.ndarray:
    """Y [r, k+1, sorties] -> EE [r, k, sorties], signe ramené au sens « facteur qui monte »."""
    r, kp1, _ = Y.shape
    k = kp1 - 1
    EE = np.zeros((r, k, Y.shape[2]))
    for j, (pts, order) in enumerate(design):
        for s, i in enumerate(order):
            d = pts[s + 1, i] - pts[s, i]
            EE[j, i] = (Y[j, s + 1] - Y[j, s]) * np.sign(d)
    return EE


def sobol_design(k: int, n: int, rng) -> np.ndarray:
    """[n, k + 2, k] : colonne 0 = A, 1 = B, 2 + i = A avec la colonne i prise dans B."""
    A, B = rng.random((n, k)), rng.random((n, k))
    X = np.empty((n, k + 2, k))
    X[:, 0], X[:, 1] = A, B
    for i in range(k):
        X[:, 2 + i] = A
        X[:, 2 + i, i] = B[:, i]
    return X


def sobol_indices(Y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Y [n, k + 2] -> (S1 [k], ST [k])."""
    Y = Y - Y[:, :2].mean()          # centrage : S1 de Saltelli 2010 n'est pas invariant par translation (ST l'est)
    yA, yB, yAB = Y[:, 0], Y[:, 1], Y[:, 2:]
    V = np.var(np.concatenate([yA, yB]))
    if V == 0:
        return np.zeros(yAB.shape[1]), np.zeros(yAB.shape[1])
    S1 = np.mean(yB[:, None] * (yAB - yA[:, None]), axis=0) / V
    ST = 0.5 * np.mean((yA[:, None] - yAB) ** 2, axis=0) / V
    return S1, ST


def bootstrap(Y: np.ndarray, rng, b: int = 500) -> tuple[np.ndarray, np.ndarray]:
    """Intervalles 2,5–97,5 % de S1 et ST : [2, k] chacun."""
    n = Y.shape[0]
    s1, st = [], []
    for _ in range(b):
        i = rng.integers(0, n, n)
        a, c = sobol_indices(Y[i])
        s1.append(a)
        st.append(c)
    q = lambda z: np.percentile(np.array(z), [2.5, 97.5], axis=0)
    return q(s1), q(st)
