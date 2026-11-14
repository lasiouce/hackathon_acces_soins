from chat import verif as V


def test_extraction_formats_francais():
    assert [v for v, _ in V.nombres("environ 1 930 kinés, entre 1 400 et 2 500 ; −18,2 % ; 0,72 ; 161 000")] == \
        [1930, 1400, 2500, -18.2, 0.72, 161000]
    assert [v for v, _ in V.nombres("en 2050 2 cas")] == [2050, 2]


def test_rattachement():
    refs = V.references({"scenario": 1930, "fourchette": [1387, 2473], "ecart_pct": 11.46, "leviers": {"quotas": 1.2},
                         "source": "Insee Omphale 2022 ; Dossier n° 76"})
    ok = "En 2050, environ 1 900 kinés (entre 1 400 et 2 500), +11 % ; places +20 % ; Dossier n° 76 ; 2 ans"
    assert V.non_rattaches(ok, refs) == []
    assert V.non_rattaches("Selon la DREES, 92 000 kinés exercent, soit 35 %", refs) == ["92 000", "35"]


def test_le_hors_horizon_n_est_pas_une_annee_admise():
    assert V.non_rattaches("en 2060 il y aura", set()) == ["2060"]
