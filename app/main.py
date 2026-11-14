"""Demo UI — projection of health professionals by département (MMOPKSI, hors médecine générale).

Run: uv run --directory app streamlit run main.py   (app/.streamlit/config.toml holds the theme)
Three personas share one engine (app/engine.py, any estimator in sante.estimators), one page each:
ARS/DG, Administration, Élu·e; plus a Méthode page.
"""
import re
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import data as D
import engine as E
import levers as LV

st.set_page_config(page_title="Professionnels de santé — projections", layout="wide", page_icon="📊")

NAVY, ACCENT, GREY, BAND = "#14234B", "#3B5BA9", "#9AA5B1", "#DCE3F1"
MAP_SCALE = ["#EEF2F9", "#C5D2EA", "#8EA7D4", "#4F6FB3", "#14234B"]
pio.templates["sante"] = go.layout.Template(layout=dict(
    font=dict(family="Helvetica Neue, Arial, sans-serif", color=NAVY, size=12),
    paper_bgcolor="white", plot_bgcolor="white", colorway=[NAVY, ACCENT, GREY],
    xaxis=dict(showgrid=False, linecolor="#C9D1E0", ticks="outside", tickcolor="#C9D1E0"),
    yaxis=dict(gridcolor="#EDF0F6", zeroline=False),
    hoverlabel=dict(bgcolor="white", bordercolor=NAVY, font_color=NAVY),
))
pio.templates.default = "plotly_white+sante"

CSS = f"""
<style>
.stApp {{ background: #F4F6FB; }}
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"] {{ display: none; }}
header[data-testid="stHeader"] {{ background: {NAVY}; }}
header[data-testid="stHeader"] a, header[data-testid="stHeader"] span, header[data-testid="stHeader"] p {{ color: #fff !important; }}
.block-container {{ padding-top: 4.2rem; max-width: 1320px; }}
.hero {{ background: linear-gradient(180deg, #E4EAF5 0%, #F4F6FB 100%); border-radius: 0 0 18px 18px;
        padding: 1.4rem 1.6rem 1.1rem; margin: -1rem -1rem 1rem; }}
.hero .kicker {{ font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; color: {ACCENT}; font-weight: 700; }}
.hero h1 {{ font-size: 2.0rem; margin: .1rem 0 .3rem; color: {NAVY}; padding: 0; }}
.hero p {{ margin: 0; color: #3D4A66; max-width: 900px; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ background: #fff; border-radius: 16px; border: 1px solid #E1E6F0;
        box-shadow: 0 2px 10px rgba(20,35,75,.05); }}
.card-band {{ background: {NAVY}; color: #fff; border-radius: 12px; padding: .55rem 1rem; font-weight: 700;
        font-size: 1.05rem; margin-bottom: .6rem; display: inline-block; }}
.card-title {{ font-weight: 700; font-size: 1.12rem; color: {NAVY}; margin-bottom: 0; }}
.crumb {{ font-size: .82rem; font-weight: 600; color: #4A5878; margin-bottom: .5rem; }}
.crumb b {{ color: {ACCENT}; }}
.src {{ font-size: .78rem; color: #66728C; border-top: 1px solid #EDF0F6; padding-top: .45rem; margin-top: .3rem; }}
.src a {{ color: {ACCENT}; }}
.kpi {{ background: #fff; border: 1px solid #E1E6F0; border-radius: 14px; padding: .8rem 1rem; height: 100%; }}
.kpi .l {{ font-size: .78rem; color: #4A5878; font-weight: 600; }}
.kpi .v {{ font-size: 1.9rem; font-weight: 700; color: {NAVY}; line-height: 1.15; }}
.kpi .s {{ font-size: .8rem; color: #66728C; }}
.pill {{ display: inline-block; background: #E4EAF5; color: {NAVY}; border-radius: 999px; padding: .15rem .7rem;
        font-size: .78rem; font-weight: 700; }}
.hyp {{ background: #F7F9FC; border-left: 3px solid {ACCENT}; border-radius: 6px; padding: .5rem .8rem;
        font-size: .88rem; color: #3D4A66; margin: .3rem 0 .6rem; }}
.say {{ font-size: 1.12rem; line-height: 1.6; color: {NAVY}; }}
.say li {{ margin-bottom: .5rem; }}
.muted {{ color: #8A94A8; }}
</style>
"""

LEVERS_DOC = D.ROOT / "docs" / "lab" / "levers.md"
STATE_KEYS = ["prof", "spec", "sector", "year", "est", "cmp", "region", "dep", "view"]
POP_LABELS = {"central": "centrale", "pop_haute": "haute", "pop_basse": "basse"}


# ---------------------------------------------------------------- data
@st.cache_data(show_spinner="Chargement des données…")
def load():
    d = D.load_all()
    d["raw"] = pd.read_parquet(D.PROCESSED / "stock.parquet",
                               columns=["profession", "source", "specialty", "mode3", "dep", "sex", "age_lo", "year", "n"])
    d["pops"] = {s: D.population(d["pop"], s) for s in POP_LABELS}
    return d


@st.cache_data(show_spinner=False)
def geo():
    return D.geometry()


@st.cache_data(show_spinner=False)
def stock_t(prof, sector, specialty):
    return E.table(load()["raw"], prof, sector, specialty)


@st.cache_data(show_spinner="Estimation en cours…")
def estimate(prof, sector, specialty, est, fit_len=6, origin=None, levers=()):
    """Headcount (point, low, high) dep × year, origin, self-backtest table, levers without effect.

    `levers` = tuple of (key, value). The band is the baseline estimator's (assumed unchanged by the levers).
    """
    t = stock_t(prof, sector, specialty)
    n, origin, ignored = E.run(est, t, fit_len, origin=origin, prof_key=prof, levers=dict(levers))
    bt = band(prof, sector, specialty, est, fit_len, origin)
    lo, hi = E.interval(n, origin, bt)
    return n, lo, hi, origin, bt, ignored


@st.cache_data(show_spinner=False)
def band(prof, sector, specialty, est, fit_len, origin):
    return E.band_table(est, stock_t(prof, sector, specialty), fit_len, origin=origin)


@st.cache_data(show_spinner=False)
def lever_registry():
    """Rows of the team's lever registry (docs/lab/levers.md), grouped by section."""
    if not LEVERS_DOC.exists():
        return pd.DataFrame()
    rows, section = [], ""
    for line in LEVERS_DOC.read_text().splitlines():
        if line.startswith("### "):
            section = line[4:].strip()
        elif re.match(r"^\| L\d+ ", line):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 8:
                rows.append(dict(section=section, id=c[0], nom=c[1], personas=c[2], slot=c[3], mecanisme=c[4],
                                 defaut=c[5], source=c[6], delai=c[7]))
    return pd.DataFrame(rows)


def parse_range(txt):
    """'1.0 · 0.9–1.3 · × …' -> (1.0, 0.9, 1.3, unit) or None."""
    parts = [p.strip() for p in txt.replace("−", "-").split("·")]
    if len(parts) < 2:
        return None
    try:
        dflt = float(parts[0])
        lo, hi = [float(x) for x in re.split(r"\s*(?:–|to)\s*", parts[1])[:2]]
    except ValueError:
        return None
    return dflt, lo, hi, (parts[2] if len(parts) > 2 else "")


# ---------------------------------------------------------------- wording (docs/lab/lexicon.md)
def fmt(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", " ")


def compare_word(v, ref, tol=0.05):
    """supérieure / inférieure à la moyenne, or proche (within ±tol)."""
    r = v / ref - 1
    if r > tol:
        return "supérieure à"
    if r < -tol:
        return "inférieure à"
    return "proche de"


def change_words(v0, v1):
    r = v1 / v0 - 1 if v0 else 0.0
    if abs(r) < 0.01:
        return "reste stable"
    return f"{'augmente' if r > 0 else 'diminue'} de {fmt(abs(r) * 100)} %"


def range_words(lo, hi):
    return f"entre {fmt(lo)} et {fmt(hi)}"


def band_label(bt, origin, year):
    """Plain description of the band used at `year`, with its horizon."""
    if year <= origin:
        return "valeur observée"
    h = year - origin
    _, _, prov = E.band_for(bt, h)
    return f"fourchette 10–90 % à {h} an{'s' if h > 1 else ''}, {prov}"


# ---------------------------------------------------------------- building blocks
def hero(kicker, title, text):
    st.markdown(f'<div class="hero"><div class="kicker">{kicker}</div><h1>{title}</h1><p>{text}</p></div>',
                unsafe_allow_html=True)


def card_head(title, crumb):
    st.markdown(f'<div class="card-title">{title}</div><div class="crumb">{crumb}</div>', unsafe_allow_html=True)


def source_line(extra=""):
    st.markdown(f'<div class="src">Sources : DREES, démographie des professionnels de santé (RPPS, ADELI, SNDS), '
                f'millésime 2026-07-02 · Insee, Omphale 2022{extra} · '
                f'<a href="/methode" target="_self">Méthode</a></div>', unsafe_allow_html=True)


def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                 f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


def hypotheses(est):
    st.markdown(f'<div class="hyp"><b>Hypothèses — {E.label(est)}.</b> {E.assumptions(est)}</div>',
                unsafe_allow_html=True)


def keep_state():
    """Widget values survive page switches."""
    for k in STATE_KEYS:
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]
    for k, v in dict(prof="specialistes", spec="Toutes", sector="liberal", year=2035, est=E.DEFAULT, cmp=[],
                     region="84", dep="63", view="Densité").items():
        st.session_state.setdefault(k, v)


def filters(estimator=True):
    """Filter bar shared by every page. Returns the selection as a dict."""
    with st.container(border=True):
        cols = st.columns([2.4, 1.6, 1.5, 2.3, 2.0] if estimator else [2.4, 1.6, 1.5, 2.2])
        prof = cols[0].selectbox("Profession", list(D.PROFESSIONS), key="prof",
                                 format_func=lambda k: D.PROFESSIONS[k][0])
        if prof == "specialistes":
            spec = cols[1].selectbox("Spécialité", ["Toutes"] + D.SPECIALTIES, key="spec")
        else:
            cols[1].selectbox("Spécialité", ["—"], disabled=True, key="_spec_off")
            spec = "Toutes"
        if prof == "infirmiers":
            cols[2].selectbox("Exercice", ["Libéral"], disabled=True, key="_sector_off")
            sector = "liberal"
        else:
            sector = cols[2].selectbox("Exercice", list(D.SECTORS), format_func=D.SECTORS.get, key="sector")
        est = E.DEFAULT
        if estimator:
            est = cols[3].selectbox("Estimateur", list(E.REGISTRY), key="est", format_func=E.label)
        year = cols[-1].slider("Année", 2012, D.HORIZON, key="year")
    specialty = None if spec in ("Toutes", "—") else spec
    label = D.PROFESSIONS[prof][0].split(" (")[0] if not specialty else f"Spécialistes — {specialty}"
    sector_label = "Libéraux" if sector == "liberal" else "Tous modes d'exercice"
    return dict(prof=prof, specialty=specialty, sector=sector, est=est, year=year, label=label,
                sector_label=sector_label)


def crumb(f, territory, origin, extra=""):
    status = f"projection · {E.label(f['est'])}" if f["year"] > origin else "observé"
    return (f'{f["label"]} | {f["sector_label"]} | {territory} | <b>{f["year"]}</b> · {status}'
            f'{" · " + extra if extra else ""}')


CHART = dict(width="stretch", theme=None, config={"displayModeBar": False})


# ---------------------------------------------------------------- charts
def choropleth(values, deps, unit, locations=None, height=520):
    df = values.rename("v").to_frame().join(deps)
    if locations is not None:
        df = df.loc[df.index.intersection(locations)]
    df["region_name"] = df["region"].map(D.REGIONS)
    fig = px.choropleth(
        df.reset_index(), geojson=geo(), locations="dep", featureidkey="properties.code", color="v",
        color_continuous_scale=MAP_SCALE, hover_name="dep_name",
        range_color=(df["v"].quantile(0.02), df["v"].quantile(0.95)),  # Paris would flatten the scale
        hover_data={"dep": False, "region_name": True, "v": ":,.0f"},
        labels={"v": unit, "region_name": "Région"},
    )
    if locations is None:  # metropole frame; outre-mer départements are reached via the region zoom
        fig.update_geos(visible=False, projection_type="mercator", lonaxis_range=[-5.5, 10], lataxis_range=[41, 51.5])
    else:
        fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(marker_line_color="white", marker_line_width=0.6)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=height,
                      coloraxis_colorbar=dict(title=dict(text=unit, side="top"), orientation="h", y=-0.02,
                                              len=0.55, thickness=10, x=0.5))
    return fig


def ranking(values, deps, ref=None, ref_label="France", unit="", text=None, color=ACCENT, lo=None, hi=None):
    """Horizontal bars, largest on top; optional lo/hi whiskers (the projection band)."""
    df = values.rename("v").to_frame().join(deps).sort_values("v")
    err = None
    if lo is not None:
        lo_, hi_ = lo.reindex(df.index), hi.reindex(df.index)
        err = dict(type="data", array=hi_ - df["v"], arrayminus=df["v"] - lo_, color="#8A94A8", thickness=1.2, width=3)
    fig = go.Figure(go.Bar(x=df["v"], y=df["dep_name"], orientation="h", marker_color=color, error_x=err,
                           text=text(df["v"]) if text else [fmt(v) for v in df["v"]], textposition="inside",
                           insidetextanchor="end", textfont=dict(color="white"),
                           cliponaxis=False, hovertemplate="%{y} : %{x:,.0f} " + unit + "<extra></extra>"))
    if ref is not None:
        fig.add_vline(x=ref, line_dash="dot", line_color=NAVY,
                      annotation_text=f"{ref_label} {fmt(ref)}", annotation_position="top")
    fig.update_layout(height=max(240, 26 * len(df) + 60), margin=dict(l=10, r=20, t=24, b=0),
                      xaxis=dict(visible=False), yaxis=dict(automargin=True, ticksuffix="  "), bargap=0.35)
    return fig


def evolution(series, origin, unit, band=None, height=360, legend=True):
    """Lines with observed (solid) and projected (dashed) parts; optional (lo, hi) band on the first series."""
    fig = go.Figure()
    if band is not None:
        lo, hi = band
        xs = [y for y in lo.index if y >= origin]
        fig.add_scatter(x=xs + xs[::-1], y=list(hi[xs]) + list(lo[xs][::-1]), fill="toself", fillcolor=BAND,
                        line_width=0, hoverinfo="skip", name="Fourchette 10–90 % (rétro-test)")
    colors = [NAVY, GREY, ACCENT]
    for i, (name, s) in enumerate(series.items()):
        obs, proj = s[s.index <= origin], s[s.index >= origin]
        w = 3 if i == 0 else 2
        fig.add_scatter(x=obs.index, y=obs, name=name, line=dict(color=colors[i], width=w),
                        hovertemplate="%{x} : %{y:,.0f} " + unit + "<extra>" + name + "</extra>")
        fig.add_scatter(x=proj.index, y=proj, name=f"{name} (projection)", showlegend=False,
                        line=dict(color=colors[i], width=w, dash="dash"),
                        hovertemplate="%{x} : %{y:,.0f} " + unit + "<extra>" + name + " · projection</extra>")
    fig.add_vline(x=origin + 0.5, line_color="#C9D1E0")
    for x, txt, anchor in [(origin + 0.8, "projection →", "left"), (origin + 0.2, "← observé", "right")]:
        fig.add_annotation(x=x, y=1.05, yref="paper", text=txt, showarrow=False, xanchor=anchor,
                           font=dict(color="#66728C", size=11))
    fig.update_layout(height=height, margin=dict(l=0, r=10, t=30, b=0), showlegend=legend,
                      legend=dict(orientation="h", y=-0.15), yaxis_title=unit)
    return fig


def region_view(n, lo, hi, pop, deps_sel, is_d):
    """Aggregate dep tables to the selection: density (per 100k) or headcount. Bounds are summed (conservative)."""
    if is_d:
        return [D.national_density(x, pop, deps_sel) for x in (n, lo, hi)]
    return [x.loc[x.index.intersection(deps_sel)].sum() for x in (n, lo, hi)]


# ---------------------------------------------------------------- pages
def page_ars():
    d = load()
    deps, pop = d["deps"], d["pops"]["central"]
    hero("Vue régionale · ARS / DG", "Ma région",
         "Effectifs et densités des professionnels de santé par département, observés depuis 2012 et projetés "
         "jusqu'en 2040 par l'estimateur choisi, avec une fourchette mesurée sur le passé.")
    f = filters()
    t0 = time.perf_counter()
    n, lo, hi, origin, bt, _ = estimate(f["prof"], f["sector"], f["specialty"], f["est"])
    dens, dlo, dhi = (D.density(x, pop) for x in (n, lo, hi))
    year = f["year"]
    reg_codes = sorted(D.REGIONS, key=D.REGIONS.get)
    reg = st.selectbox("Région", reg_codes, key="region", format_func=D.REGIONS.get)
    rname = D.REGIONS[reg]
    reg_deps = deps.index[deps["region"] == reg].intersection(n.index)
    nat = D.national_density(n, pop)
    rd, rdl, rdh = region_view(n, lo, hi, pop, reg_deps, True)
    projected = year > origin

    k = st.columns(4)
    kpi(k[0], f"Densité {rname}, {year}", fmt(rd[year]),
        f"pour 100 000 hab. · {range_words(rdl[year], rdh[year])}" if projected else "pour 100 000 habitants")
    kpi(k[1], f"Densité France, {year}", fmt(nat[year]), "pour 100 000 habitants")
    kpi(k[2], "Écart à la moyenne nationale", f"{(rd[year] / nat[year] - 1) * 100:+.1f} %".replace("-", "−"),
        f"densité {compare_word(rd[year], nat[year])} la moyenne")
    kpi(k[3], f"Effectif {rname}, {year}", fmt(n.loc[reg_deps, year].sum()), f["sector_label"])
    st.write("")
    hypotheses(f["est"])

    with st.container(border=True):
        h1, h2 = st.columns([4, 1.3])
        h1.markdown('<div class="card-band">Effectif et densité</div>', unsafe_allow_html=True)
        view = h2.segmented_control("Voir", ["Effectif", "Densité"], key="view", label_visibility="collapsed") or "Densité"
        is_d = view == "Densité"
        vals, vlo, vhi = (dens, dlo, dhi) if is_d else (n, lo, hi)
        unit = "pour 100 000 hab." if is_d else "professionnels"
        t1, t2, t3 = st.tabs([f"{year}", "Évolution", "Comparer les estimateurs"])
        with t1:
            card_head(f"{view} par département", crumb(f, rname, origin, band_label(bt, origin, year)))
            c1, c2 = st.columns([1.15, 1])
            c1.plotly_chart(choropleth(vals[year], deps, unit, locations=reg_deps), **CHART)
            c2.plotly_chart(ranking(vals.loc[reg_deps, year], deps, nat[year] if is_d else None, unit=unit,
                                    lo=vlo[year] if projected else None, hi=vhi[year] if projected else None),
                            **CHART)
            if projected:
                st.caption("Traits gris : fourchette 10–90 % de chaque département.")
        with t2:
            card_head(f"{view} — {rname}" + (" et France" if is_d else ""), crumb(f, rname, origin, "2012–2040"))
            m, mlo, mhi = region_view(n, lo, hi, pop, reg_deps, is_d)
            series = {rname: m, "France": nat} if is_d else {rname: m}
            st.plotly_chart(evolution(series, origin, unit, (mlo, mhi)), **CHART)
            st.caption(f"Fourchette : erreurs relatives 10–90 % de l'estimateur quand on le relance {bt.index.min()} à "
                       f"{bt.index.max()} ans plus tôt (rétro-test sur les départements) ; au-delà de "
                       f"{bt.index.max()} ans, extrapolée linéairement. Bornes départementales additionnées.")
        with t3:
            others = [k for k in E.REGISTRY if k != f["est"]]
            cmp = st.multiselect("Comparer avec (2 au plus)", others, key="cmp", max_selections=2,
                                 format_func=E.label, placeholder="Choisir un ou deux estimateurs")
            keys = [f["est"]] + [k for k in cmp if k in others]
            runs = {}
            for key in keys:
                cn, clo, chi, co, _, _ = estimate(f["prof"], f["sector"], f["specialty"], key)
                runs[key] = (*region_view(cn, clo, chi, pop, reg_deps, is_d), co)
            ymax = 1.05 * max(max(r[0].max(), r[2].max()) for r in runs.values())
            ymin = 0.95 * min(min(r[0].min(), r[1].min()) for r in runs.values())
            cols = st.columns(len(keys))
            for col, key in zip(cols, keys):
                with col:
                    m, mlo, mhi, co = runs[key]
                    st.markdown(f'<span class="pill">{E.label(key)}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi" style="margin:.5rem 0"><div class="l">{rname}, {year}</div>'
                                f'<div class="v">{fmt(m[year])}</div><div class="s">{unit}'
                                f'{" · " + range_words(mlo[year], mhi[year]) if year > co else ""}</div></div>',
                                unsafe_allow_html=True)
                    st.plotly_chart(evolution({rname: m}, co, unit, (mlo, mhi), height=260, legend=False)
                                    .update_yaxes(range=[ymin, ymax]), **CHART)  # same scale across columns
                    st.caption(E.assumptions(key))
        st.caption(f"Calcul : {fmt((time.perf_counter() - t0) * 1000)} ms")
        source_line(" · Fond de carte : france-geojson d'après IGN Admin Express")


def page_admin():
    d = load()
    deps = d["deps"]
    hero("Administration", "Tous les paramètres",
         "Choix de l'estimateur, de sa fenêtre d'ajustement et de l'année d'origine ; la fourchette est mesurée "
         "en relançant l'estimateur sur le passé. Les leviers câblés agissent à travers l'estimateur choisi.")
    f = filters(estimator=False)
    t = stock_t(f["prof"], f["sector"], f["specialty"])
    first, latest = int(t["year"].min()), int(t["year"].max())
    c1, c2 = st.columns([1, 1.6])
    with c1, st.container(border=True):
        st.markdown('<div class="card-band">Paramètres de l\'estimation</div>', unsafe_allow_html=True)
        est = st.selectbox("Estimateur", list(E.REGISTRY), key="est", format_func=E.label)
        hypotheses(est)
        fit_len = st.slider("Fenêtre d'ajustement (années)", 3, 10, 6,
                            help="Années de données utilisées pour estimer les taux ou la tendance.")
        origin = st.slider("Année d'origine", first + 3, latest, latest,
                           help="Dernière année de données utilisée. Une origine passée permet de comparer "
                                "la projection aux effectifs observés ensuite.")
        pop_scen = st.selectbox("Variante de population (Omphale 2022)", list(POP_LABELS),
                                format_func=lambda s: f"Population {POP_LABELS[s]}")
        st.caption(f"Données disponibles : {first}–{latest}.")
    with c1, st.container(border=True):
        st.markdown('<div class="card-band">Leviers câblés</div>', unsafe_allow_html=True)
        st.caption("Valeur par défaut = statu quo. Effets : hypothèses, sauf mention.")
        vals = {}
        for lv in LV.LEVERS:
            name = lv.name
            if lv.key == "entries":
                name += f" — {LV.ENTRY_ID[f['prof']]}, effet après {LV.LAG[f['prof']]} ans de formation"
            else:
                name = f"{lv.ids} · {name}"
            vals[lv.key] = st.slider(f"{name} ({lv.unit})", lv.lo, lv.hi, lv.default, lv.step, key=f"lv_{lv.key}",
                                     help=f"{lv.mechanism} Source : {lv.source}")
        if st.button("Revenir au statu quo"):
            for lv in LV.LEVERS:
                st.session_state[f"lv_{lv.key}"] = lv.default
            st.rerun()
    t0 = time.perf_counter()
    act = tuple(sorted(LV.active(vals).items()))
    n, lo, hi, origin, bt, ignored = estimate(f["prof"], f["sector"], f["specialty"], est, fit_len, origin, act)
    ms = (time.perf_counter() - t0) * 1000
    base_n = estimate(f["prof"], f["sector"], f["specialty"], est, fit_len, origin)[0] if act else n
    pop = d["pops"][pop_scen]
    dens = D.density(n, pop)
    nat, nlo, nhi = (D.national_density(x, pop) for x in (n, lo, hi))
    year = f["year"]
    f["est"] = est
    with c2, st.container(border=True):
        st.markdown('<div class="card-band">Résultat</div>', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs([f"{year}", "Évolution", "Rétro-test"])
        with t1:
            card_head("Densité par département", crumb(f, "France", origin, band_label(bt, origin, year)))
            st.plotly_chart(choropleth(dens[year], deps, "pour 100 000 hab.", height=470), **CHART)
        with t2:
            card_head("Densité France", crumb(f, "France", origin, "2012–2040"))
            obs = D.national_density(stock_t(f["prof"], f["sector"], f["specialty"])
                                     .groupby(["dep", "year"])["n"].sum().unstack("year"), pop)
            fig = evolution({"Projection": nat}, origin, "pour 100 000 hab.", (nlo, nhi))
            if origin < latest:
                after = obs[obs.index > origin]
                fig.add_scatter(x=after.index, y=after, name="Observé après l'origine", mode="lines+markers",
                                line=dict(color=GREY, width=2))
            st.plotly_chart(fig, **CHART)
        with t3:
            card_head("Erreur relative par horizon", "projection ÷ observé − 1, sur les départements de "
                      f"≥ {E.MIN_N} professionnels · 10e, 50e et 90e centiles")
            tb = bt.assign(**{c: (bt[c] * 100).round(1) for c in ["q10", "q50", "q90"]}).rename(
                columns={"q10": "10 % (%)", "q50": "médiane (%)", "q90": "90 % (%)", "n_dep": "départements",
                         "backtest": "relance"})
            st.dataframe(tb, width="stretch")
        if act and year > origin:
            dn = n[year].sum() - base_n[year].sum()
            st.markdown(f'<div class="hyp"><b>Effet projeté des leviers en {year}</b> : '
                        f'{"+" if dn >= 0 else "−"}{fmt(abs(dn))} professionnels '
                        f'({(n[year].sum() / base_n[year].sum() - 1) * 100:+.1f} %) par rapport au statu quo, '
                        f'même estimateur.'
                        + (f' Sans effet sur cet estimateur : {", ".join(LV.BY_KEY[k].ids for k in ignored)} '
                           f'(il ne modélise pas les entrées et sorties).' if ignored else '') + '</div>',
                        unsafe_allow_html=True)
        st.caption(f"Densité France {year} : {fmt(nat[year])} pour 100 000 hab."
                   f"{' (' + range_words(nlo[year], nhi[year]) + ')' if year > origin else ''} · calcul : {fmt(ms)} ms")
        source_line()

    with st.container(border=True):
        st.markdown('<div class="card-band">Registre des leviers</div>', unsafe_allow_html=True)
        reg = lever_registry()
        if reg.empty:
            st.caption("docs/lab/levers.md introuvable.")
        else:
            wired = {"L01", "L02", "L03", "L04", "L05", "L06", "L09", "L10", "L14", "L32"}
            card_head(f"{len(reg)} leviers · {len(wired & set(reg['id']))} câblés",
                      "Source : registre de l'équipe, docs/lab/levers.md · valeur par défaut = statu quo")
            for section, grp in reg.groupby("section", sort=False):
                with st.expander(f"{section} — {len(grp)} leviers"):
                    for _, r in grp.iterrows():
                        a, b = st.columns([1.3, 2])
                        rng = parse_range(r["defaut"])
                        lab = f"{r['id']} · {r['nom']}"
                        if r["id"] in wired:
                            a.markdown(f"**{lab}**  \n<span class='pill'>câblé</span>", unsafe_allow_html=True)
                        elif rng and rng[1] < rng[2]:
                            dflt, lo_, hi_, unitx = rng
                            a.slider(lab, lo_, hi_, min(max(dflt, lo_), hi_), disabled=True,
                                     help=f"Non câblé. Unité : {unitx}", key=f"lev_{r['id']}")
                        else:
                            a.markdown(f"**{lab}**  \n<span class='muted'>{r['defaut']}</span>",
                                       unsafe_allow_html=True)
                        b.markdown(f"<span class='muted'>Mécanisme :</span> {r['mecanisme']}  \n"
                                   f"<span class='muted'>Source :</span> {r['source']}", unsafe_allow_html=True)
    with st.expander("Tableau par département"):
        tab = pd.DataFrame({"effectif": n[year], "bas": lo[year], "haut": hi[year], "densité": dens[year]}).join(deps)
        tab["écart vs France (%)"] = (tab["densité"] / nat[year] - 1) * 100
        st.dataframe(tab.round(1).sort_values("densité"), width="stretch")


def page_elu():
    d = load()
    deps = d["deps"]
    est = E.DEFAULT
    hero("En bref", "Mon territoire",
         "Une lecture en quelques phrases : la densité de professionnels, comparée à la moyenne nationale et "
         "régionale, avec la projection de référence.")
    f = filters(estimator=False)
    f["est"] = est
    n, lo, hi, origin, bt, _ = estimate(f["prof"], f["sector"], f["specialty"], est)
    pop = d["pops"]["central"]
    dens, dlo, dhi = (D.density(x, pop) for x in (n, lo, hi))
    year = f["year"]
    order = deps.assign(rn=deps["region"].map(D.REGIONS)).sort_values(["rn", "dep_name"])
    dep = st.selectbox("Territoire", list(order.index), key="dep",
                       format_func=lambda c: f"{order.loc[c, 'rn']} › {order.loc[c, 'dep_name']}")
    name = deps.loc[dep, "dep_name"]
    ref_year = min(origin, 2024)
    nat = D.national_density(n, pop)
    reg_deps = deps.index[deps["region"] == deps.loc[dep, "region"]].intersection(n.index)
    rv = D.national_density(n, pop, reg_deps)[year]
    v, v0, ref = dens.loc[dep, year], dens.loc[dep, ref_year], nat[year]
    projected = year > origin

    with st.container(border=True):
        st.markdown(f'<div class="card-band">{name}, {year}</div>', unsafe_allow_html=True)
        card_head(f["label"], crumb(f, name, origin, "projection de référence" if projected else ""))
        rng = f" ({range_words(dlo.loc[dep, year], dhi.loc[dep, year])})" if projected else ""
        say = [f"En {year}, la densité de {f['label'].lower()} dans le département <b>{name}</b> "
               f"{'serait' if projected else 'était'} de <b>{fmt(v)} pour 100 000 habitants</b>{rng}. "
               f"Elle est {compare_word(v, ref)} la moyenne nationale ({fmt(ref)}) "
               f"et {compare_word(v, rv)} la moyenne régionale ({fmt(rv)})."]
        if year != ref_year:
            say.append(f"Entre {ref_year} et {year}, la densité dans ce département {change_words(v0, v)} "
                       f"(France : {change_words(nat[ref_year], ref)}).")
        if compare_word(v, ref) == "inférieure à":
            say.append("C'est un territoire où la densité de ces professionnels est inférieure à la moyenne "
                       "nationale ; à besoins égaux, l'accès y est moindre.")
        st.markdown('<ul class="say">' + "".join(f"<li>{s}</li>" for s in say) + "</ul>", unsafe_allow_html=True)
        if projected:
            st.markdown(f'<div class="hyp"><b>Projection sous hypothèses.</b> {E.assumptions(est)} '
                        f'La fourchette indique l\'écart observé par le passé entre ce type de projection et '
                        f'la réalité ({band_label(bt, origin, year)}).</div>', unsafe_allow_html=True)
        k = st.columns(3)
        kpi(k[0], "Densité du département", fmt(v), "pour 100 000 habitants")
        kpi(k[1], "Moyenne nationale", fmt(ref), "pour 100 000 habitants")
        kpi(k[2], "Effectif", fmt(n.loc[dep, year]), "professionnels")
        st.write("")
        source_line()

    c1, c2 = st.columns([1.4, 1])
    with c1, st.container(border=True):
        card_head("Densité par département", crumb(f, "France", origin))
        st.plotly_chart(choropleth(dens[year], deps, "pour 100 000 hab.", height=500), **CHART)
    with c2, st.container(border=True):
        card_head("Selon la population projetée", f"{name} | densité en <b>{year}</b> | variantes Insee")
        rows = []
        for s, lab in POP_LABELS.items():
            dd = D.density(n, d["pops"][s])
            rows.append(f"<li>Avec la variante de population <b>{lab}</b>, la densité serait de "
                        f"{fmt(dd.loc[dep, year])} pour 100 000 habitants.</li>")
        st.markdown('<ul class="say" style="font-size:1rem">' + "".join(rows) + "</ul>", unsafe_allow_html=True)
        st.markdown("<span class='muted'>En préparation (registre des leviers) : Formation renforcée, "
                    "Partage des compétences, Installation orientée, Activité prolongée.</span>",
                    unsafe_allow_html=True)
        st.divider()
        card_head("Où la densité baisse le plus", f"{ref_year} → {year} | France")
        ch = ((dens[year] / dens[ref_year] - 1) * 100).dropna().sort_values().head(5)
        if (ch < 0).any():
            ch = ch[ch < 0]
            st.plotly_chart(ranking(-ch, deps, unit="% de baisse", color=GREY,  # bar length = size of the drop
                                    text=lambda s: [f"−{x:.0f} %" for x in s]), **CHART)
        else:
            st.caption("Aucun département où la densité baisse sur cette période.")


def page_methode():
    hero("Méthode", "Sources, estimateurs et limites",
         "Plusieurs algorithmes d'estimation, une même interface : aucun chiffre unique n'est présenté comme "
         "« la » projection.")
    c1, c2 = st.columns(2)
    with c1, st.container(border=True):
        st.markdown('<div class="card-band">Sources</div>', unsafe_allow_html=True)
        st.markdown(f"""
- **Effectifs** — {D.SOURCES['stock']}. Effectif au 31 décembre ; libéral = libéral + mixte. Kinés : RPPS 2017–2026 (les années ADELI rompent la série). Infirmiers : libéraux seulement (SNDS, jusqu'en 2023).
- **Population** — {D.SOURCES['population']}. Avant 2018, la valeur 2018 est reprise.
- **Fond de carte** — {D.SOURCES['geometry']}.
- **Leviers** — registre de l'équipe, `docs/lab/levers.md`.
""")
    with c2, st.container(border=True):
        st.markdown('<div class="card-band">Calcul</div>', unsafe_allow_html=True)
        st.markdown(f"""
- **Densité** = effectif ÷ population × 100 000, par département et par année.
- **Projection** : l'estimateur choisi est ajusté sur les 6 dernières années disponibles et projeté jusqu'en {D.HORIZON}. Estimateur par défaut : **{E.label(E.DEFAULT)}**.
- **Fourchette 10–90 %** : on relance le même estimateur *h* années plus tôt, on compare sa projection à l'effectif observé, et on retient les 10e et 90e centiles de l'erreur relative par département. Mesurée jusqu'à {E.MAX_BACKTEST_H} ans, extrapolée linéairement au-delà.
- Départements exclus : codes 999 (étranger) et 20 (Corse non ventilée).
""")
    with st.container(border=True):
        st.markdown('<div class="card-band">Estimateurs disponibles</div>', unsafe_allow_html=True)
        for key in E.REGISTRY:
            st.markdown(f"- **{E.label(key)}** — {E.assumptions(key)}")
    with st.container(border=True):
        st.markdown('<div class="card-band">Vocabulaire</div>', unsafe_allow_html=True)
        st.markdown("Les textes décrivent et comparent, sans jugement de valeur (`docs/lab/lexicon.md`) : "
                    "« densité **inférieure à la moyenne** », « accès **moindre** », « la densité **diminue de X %** », "
                    "« **entre** 410 **et** 450 ». Écart de ±5 % = « proche de la moyenne ».")


# ---------------------------------------------------------------- app
st.markdown(CSS, unsafe_allow_html=True)
if load()["pop"] is None:
    st.error("data/processed/population.parquet introuvable — lancer `uv run python -m sante.load`.")
    st.stop()
keep_state()
nav = st.navigation([
    st.Page(page_ars, title="Vue régionale", url_path="region", default=True),
    st.Page(page_elu, title="En bref", url_path="en-bref"),
    st.Page(page_admin, title="Tous les paramètres", url_path="parametres"),
    st.Page(page_methode, title="Méthode", url_path="methode"),
], position="top")
nav.run()
