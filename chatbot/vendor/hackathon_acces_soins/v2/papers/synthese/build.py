"""Assemble le prétirage de synthèse à partir des six prétirages d'axe (v2/papers/axe*/main.tex).

Run (depuis ce dossier) : python3 build.py && tectonic main.tex

Pour chaque axe : titre, résumé français, corps (de la première \\section jusqu'à la bibliographie) et
annexes sont extraits tels quels. Pour éviter les collisions entre articles, les étiquettes (\\label,
\\ref…), les clés de citation et les chemins de figures reçoivent un préfixe propre à l'axe ; les
bibliographies sont fusionnées avec le même préfixe. Les textes propres à la synthèse (introduction =
feuille de route, interface et UAT, suite) sont écrits à la main dans intro.tex, uat.tex et suite.tex.
Rien n'est modifié dans les dossiers des axes : relancer build.py suffit à reprendre leurs mises à jour.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
AXES = [("axe0-jumeau", "a0", "Axe 0 --- le jumeau numérique"),
        ("axe1-hyperparametres", "a1", "Axe 1 --- hyperparamètres sourcés et mesurables"),
        ("axe2-methodes", "a2", "Axe 2 --- méthodes de modélisation interprétables"),
        ("axe3-validation", "a3", "Axe 3 --- méthodologie de validation"),
        ("axe4-donnees", "a4", "Axe 4 --- données"),
        ("axe5-sensibilite", "a5", "Axe 5 --- sensibilité et incertitude")]
PREAMBLE_KEEP = re.compile(r"^\\(usepackage|usetikzlibrary|usepgfplotslibrary|pgfplotsset|newcommand|renewcommand|DeclareMathOperator)")


def braced(s: str, start: int) -> tuple[str, int]:
    """Contenu de l'accolade ouvrante en s[start] (accolades équilibrées) et position après la fermante."""
    depth, i = 0, start
    while i < len(s):
        if s[i] == "{" and s[i - 1] != "\\":
            depth += 1
        elif s[i] == "}" and s[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
        i += 1
    raise ValueError("accolade non fermée")


def prefix_keys(tex: str, p: str, axdir: str) -> str:
    tex = re.sub(r"\\label\{([^}]*)\}", lambda m: f"\\label{{{p}-{m.group(1)}}}", tex)
    tex = re.sub(r"\\(ref|eqref|autoref|pageref|cref|Cref|nameref)\{([^}]*)\}",
                 lambda m: f"\\{m.group(1)}{{{','.join(p + '-' + k.strip() for k in m.group(2).split(','))}}}", tex)
    tex = re.sub(r"\\(cite[a-zA-Z]*)((?:\[[^\]]*\])*)\{([^}]*)\}",
                 lambda m: f"\\{m.group(1)}{m.group(2)}{{{','.join(p + '-' + k.strip() for k in m.group(3).split(',') if k.strip())}}}", tex)
    tex = re.sub(r"\\includegraphics((?:\[[^\]]*\])?)\{(?!/|\.\./)([^}]*)\}",
                 lambda m: f"\\includegraphics{m.group(1)}{{../{axdir}/{m.group(2)}}}", tex)
    tex = re.sub(r"\\input\{(?!/|\.\./)([^}]*)\}", lambda m: f"\\input{{../{axdir}/{m.group(1)}}}", tex)
    return tex


def extract(axdir: str, p: str):
    src = (HERE.parent / axdir / "main.tex").read_text(encoding="utf-8")
    pre, doc = src.split("\\begin{document}", 1)
    extras = [l.strip() for l in pre.splitlines() if PREAMBLE_KEEP.match(l.strip())]
    t = pre.index("\\title")
    title, _ = braced(pre, pre.index("{", t))
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", doc, re.S).group(1).strip()
    body = doc[doc.index("\\section"):doc.index("\\bibliographystyle")]
    appx = ""
    if "\\appendix" in doc:
        appx = doc[doc.index("\\appendix") + len("\\appendix"):doc.index("\\end{document}")]
    bib = (HERE.parent / axdir / "refs.bib").read_text(encoding="utf-8")
    bib = re.sub(r"(@\w+\s*\{\s*)([^,\s]+)\s*,", lambda m: f"{m.group(1)}{p}-{m.group(2)},", bib)
    bib = re.sub(r"(?i)@(string|comment|preamble)\s*\{\s*" + p + "-", r"@\1{", bib)
    return (title, prefix_keys(abstract, p, axdir), prefix_keys(body, p, axdir),
            prefix_keys(appx, p, axdir).strip(), bib, extras)


def main():
    parts, appendices, bibs, extras = [], [], [], []
    for axdir, p, name in AXES:
        title, abstract, body, appx, bib, ex = extract(axdir, p)
        extras += [e.replace("\\newcommand", "\\providecommand") for e in ex if e not in extras]
        title1 = re.sub(r"\\\\\s*", " ", title)
        parts.append(f"\\part{{{name}}}\n\\noindent\\textit{{Article d'origine : « {title1} » "
                     f"(\\texttt{{v2/papers/{axdir}/}}).}}\n\n"
                     f"\\begin{{quote}}\\small\\textbf{{Résumé de l'axe.}} {abstract}\\end{{quote}}\n\n{body}\n")
        if appx:
            appendices.append(f"\\section{{Annexes de l'{name.split(' ---')[0].lower()}}}\n"
                              + re.sub(r"\\section\{", r"\\subsection{", appx) + "\n")
        bibs.append(f"% ---- {axdir}\n{bib}\n")
    (HERE / "parts.tex").write_text("% Généré par build.py, ne pas modifier à la main.\n" + "\n".join(parts), encoding="utf-8")
    (HERE / "annexes.tex").write_text("% Généré par build.py, ne pas modifier à la main.\n" + "\n".join(appendices), encoding="utf-8")
    (HERE / "refs.bib").write_text("% Généré par build.py : fusion des refs.bib des axes, clés préfixées.\n" + "\n".join(bibs), encoding="utf-8")
    (HERE / "extras.tex").write_text("% Généré par build.py : paquets et macros des préambules des axes.\n" + "\n".join(extras) + "\n", encoding="utf-8")
    print(f"{len(parts)} axes, {sum(1 for b in bibs for _ in re.finditer(r'@[A-Za-z]+\s*\{', b))} entrées bibliographiques, extras : {extras}")


if __name__ == "__main__":
    main()
