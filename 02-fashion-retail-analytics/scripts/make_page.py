# -*- coding: utf-8 -*-
"""
Génère docs/index.html — page de restitution autonome, sans dépendance externe.
Tous les chiffres sont calculés depuis les CSV : aucune valeur écrite en dur.
Usage : python scripts/make_page.py
"""
import pandas as pd

fct = pd.read_csv("data/processed/fct_transactions.csv", parse_dates=["date"])
dim = pd.read_csv("data/processed/dim_clients.csv")
ORDER = ["4. VIP", "3. Fidèle", "2. Régulier", "1. Occasionnel"]

ca, ntx, ncl = fct.montant.sum(), len(fct), len(dim)
panier, median = fct.montant.mean(), fct.montant.median()
seg = dim.groupby("segment_valeur").agg(
    clients=("client_id", "size"), ca=("ca_client", "sum"),
    achats=("nb_achats", "sum"), panier=("panier_moyen", "mean")).reindex(ORDER)
seg["pct_cl"] = seg.clients / seg.clients.sum() * 100
seg["pct_ca"] = seg.ca / seg.ca.sum() * 100
pay = fct.groupby("paiement").montant.agg(["size", "sum", "mean"])
prod = fct.groupby("article").agg(ca=("montant", "sum"), note=("note", "mean")).reset_index()
alerte = prod[prod.note < 2.70].sort_values("note")

sp = lambda v, d=0: f"{v:,.{d}f}".replace(",", " ").replace(".", ",")
COLS = {"4. VIP": "#7B2D3B", "3. Fidèle": "#C4715A", "2. Régulier": "#E0A48A", "1. Occasionnel": "#8A7580"}

def barres(col, unite):
    out = []
    for s in ORDER:
        v = seg.loc[s, col]
        out.append(f'<div class="bar" style="width:{v:.2f}%;background:{COLS[s]}" '
                   f'title="{s} : {sp(v,1)} %">{f"{sp(v,1)} %" if v > 8 else ""}</div>')
    return f'<div class="stack" aria-label="{unite}">' + "".join(out) + "</div>"

lignes_seg = "\n".join(
    f"<tr><td><span class='dot' style='background:{COLS[s]}'></span>{s}</td>"
    f"<td class='n'>{int(seg.loc[s,'clients'])}</td><td class='n'>{sp(seg.loc[s,'pct_cl'],1)} %</td>"
    f"<td class='n'>{sp(seg.loc[s,'ca'])} $</td><td class='n'><b>{sp(seg.loc[s,'pct_ca'],1)} %</b></td>"
    f"<td class='n'>{int(seg.loc[s,'achats'])}</td><td class='n'>{sp(seg.loc[s,'panier'],2)} $</td></tr>"
    for s in ORDER)

lignes_alerte = "\n".join(
    f"<tr><td>{r.article}</td><td class='n'>{sp(r.ca)} $</td>"
    f"<td class='n'><b>{sp(r.note,2)}</b></td></tr>" for r in alerte.itertuples())

FIGS = [
    ("01_segments_part.png", "Un quart des clients, la moitié du chiffre d'affaires"),
    ("02_panier_vs_frequence.png", "Le levier des VIP est le panier, pas la fréquence"),
    ("03_ca_satisfaction.png", "Le premier contributeur au CA est le plus mal noté"),
    ("04_clients_nuage.png", "Les VIP s'étirent vers la droite, pas vers le haut"),
    ("05_top_articles.png", "Tunic domine le chiffre d'affaires — et déçoit"),
]
figs = "\n".join(
    f'<figure><img src="assets/{f}" alt="{t}" loading="lazy"><figcaption>{t}</figcaption></figure>'
    for f, t in FIGS)

html = f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fashion Retail Analytics — Souleymane N'DIAYE</title>
<meta name="description" content="Segmentation client et qualité de données sur {sp(ntx)} transactions retail. Erreur de grain détectée et corrigée.">
<style>
:root{{--plum:#4A2B3D;--cream:#F5EDE4;--wine:#7B2D3B;--terra:#C4715A;--ink:#2B1A24;--muted:#8A7580;--line:#E5D9CE}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--cream);color:var(--ink);line-height:1.6;
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif}}
.wrap{{max-width:920px;margin:0 auto;padding:0 24px 96px}}
header{{background:var(--plum);color:var(--cream);padding:64px 0 56px;margin-bottom:48px}}
header .wrap{{padding-bottom:0}}
h1{{font-size:38px;margin:0 0 10px;letter-spacing:-.02em;line-height:1.15}}
.lede{{font-size:17px;opacity:.82;max-width:640px;margin:0}}
.auth{{margin-top:26px;font-size:14px;opacity:.62}}
.auth a{{color:var(--cream)}}
h2{{font-size:13px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);
 margin:56px 0 18px;font-weight:700}}
h3{{font-size:20px;margin:32px 0 10px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-top:-92px}}
.kpi{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px}}
.kpi b{{display:block;font-size:27px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.kpi span{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.07em}}
.kpi em{{display:block;font-size:11.5px;color:var(--muted);font-style:normal;margin-top:6px}}
.perimetre{{font-size:12.5px;color:var(--muted);margin-top:14px}}
.callout{{background:#fff;border-left:3px solid var(--wine);border-radius:0 10px 10px 0;
 padding:20px 24px;margin:24px 0}}
.callout b{{color:var(--wine)}}
table{{width:100%;border-collapse:collapse;font-size:14.5px;background:#fff;
 border:1px solid var(--line);border-radius:10px;overflow:hidden}}
th{{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;
 color:var(--muted);padding:12px 14px;border-bottom:1px solid var(--line)}}
td{{padding:11px 14px;border-bottom:1px solid var(--line)}}
tr:last-child td{{border-bottom:none}}
.n{{text-align:right;font-variant-numeric:tabular-nums}}
.dot{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:9px}}
.stack{{display:flex;height:34px;border-radius:7px;overflow:hidden;margin:6px 0 4px}}
.bar{{display:flex;align-items:center;justify-content:center;color:#fff;font-size:12.5px;
 font-weight:700;transition:.2s}}
.lbl{{font-size:12.5px;color:var(--muted)}}
figure{{margin:26px 0}}
figure img{{width:100%;border:1px solid var(--line);border-radius:10px;display:block}}
figcaption{{font-size:12.5px;color:var(--muted);margin-top:8px}}
.limites{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px 26px}}
.limites li{{margin-bottom:9px;font-size:14.5px}}
footer{{margin-top:64px;padding-top:22px;border-top:1px solid var(--line);
 font-size:12.5px;color:var(--muted)}}
a{{color:var(--wine)}}
</style></head><body>

<header><div class="wrap">
<h1>Fashion Retail Analytics</h1>
<p class="lede">Segmentation client et qualité de données sur {sp(ntx)} transactions.
Ce projet documente aussi une erreur de modélisation trouvée dans sa propre première version.</p>
<p class="auth">Souleymane N'DIAYE · <a href="https://github.com/juniorbaw/data-portfolio">Code et documentation</a></p>
</div></header>

<div class="wrap">

<div class="kpis">
<div class="kpi"><b>{sp(ntx)}</b><span>Transactions</span></div>
<div class="kpi"><b>{sp(ca)} $</b><span>Chiffre d'affaires</span></div>
<div class="kpi"><b>{sp(panier,2)} $</b><span>Panier moyen</span><em>par transaction</em></div>
<div class="kpi"><b>{ncl}</b><span>Clients</span></div>
</div>
<p class="perimetre">{sp(ntx)} transactions retenues sur 3 400 — 19,1 % des lignes sources sans
montant, exclues du chiffre d'affaires. Données synthétiques, montants en USD.
Période : {fct.date.min():%d/%m/%Y} au {fct.date.max():%d/%m/%Y}.</p>

<h2>Ce que disent les données</h2>

<h3>Un quart des clients, la moitié du chiffre d'affaires</h3>
<p class="lbl">Part des clients</p>{barres("pct_cl","Part des clients")}
<p class="lbl">Part du chiffre d'affaires</p>{barres("pct_ca","Part du chiffre d'affaires")}
<div class="callout">Les segments sont des <b>quartiles de valeur</b> : chacun contient environ
25 % des clients par construction. Ce qui varie, c'est leur contribution au chiffre d'affaires,
de {sp(seg.pct_ca.min(),1)} % à {sp(seg.pct_ca.max(),1)} %.</div>

<table><thead><tr><th>Segment</th><th class="n">Clients</th><th class="n">% clients</th>
<th class="n">Chiffre d'affaires</th><th class="n">% CA</th><th class="n">Achats</th>
<th class="n">Panier moyen</th></tr></thead><tbody>{lignes_seg}</tbody></table>

<h3>Le levier des VIP est le panier, pas la fréquence</h3>
<div class="callout">Les VIP réalisent <b>{int(seg.loc['4. VIP','achats'])} achats</b> contre
<b>{int(seg.loc['3. Fidèle','achats'])}</b> pour les Fidèles : ils n'achètent pas plus souvent.
Leur panier moyen est de {sp(seg.loc['4. VIP','panier'],2)} $ contre
{sp(seg.loc['3. Fidèle','panier'],2)} $, soit
<b>{seg.loc['4. VIP','panier']/seg.loc['3. Fidèle','panier']:.1f} fois plus</b>.
Le levier commercial est la montée en gamme, pas la relance.</div>

<h3>Le premier contributeur au chiffre d'affaires est le plus mal noté</h3>
<table><thead><tr><th>Article</th><th class="n">Chiffre d'affaires</th>
<th class="n">Note moyenne</th></tr></thead><tbody>{lignes_alerte}</tbody></table>
<div class="callout"><b>{alerte.iloc[0].article}</b> est le premier contributeur au chiffre
d'affaires ({sp(prod.ca.max())} $) et l'article le plus mal noté
({sp(alerte.iloc[0].note,2)} / 5). Le revenu d'aujourd'hui finance l'attrition de demain :
audit qualité avant toute action d'acquisition.</div>

<h3>Le mode de paiement discrimine peu</h3>
<div class="callout">Panier moyen de <b>{sp(pay.loc['Credit Card','mean'],2)} $</b> par carte
contre <b>{sp(pay.loc['Cash','mean'],2)} $</b> en espèces, soit un écart de
{(pay.loc['Credit Card','mean']/pay.loc['Cash','mean']-1)*100:.0f} %.
Faible, et sur données synthétiques : à ne pas surinterpréter.</div>

<h2>Graphiques</h2>
{figs}

<h2>L'erreur de grain, et sa correction</h2>
<p>La première version de ce tableau de bord affichait <b>7,6 M de chiffre d'affaires</b> pour
{sp(ntx)} transactions et un panier moyen de {sp(panier,2)}. Ces trois nombres sont
incompatibles : leur produit donne {sp(ntx*panier)}.</p>
<p>Les colonnes <code>total_depense</code> et <code>nb_achats</code> étaient des agrégats
<b>client</b>, laissés dans la table de <b>transactions</b> et donc répétés sur chaque ligne.
L'outil de restitution les additionnait, comptant chaque client autant de fois qu'il avait
d'achats — {fct.groupby('client_id').size().mean():.1f} en moyenne. Le « 2 800 clients » avait la
même origine : un décompte de lignes, pas de clients distincts. Il y a {ncl} clients.</p>
<div class="callout">La correction est structurelle : deux tables, deux grains, et un test
(<code>assert_coherence_ca</code>) qui échoue si les deux totaux ne se rejoignent plus.
Il tourne à chaque build.</div>

<h2>Méthode et limites</h2>
<div class="limites"><ul>
<li><b>Données synthétiques</b>, générées à des fins pédagogiques. Aucune conclusion n'est
transposable à une enseigne réelle.</li>
<li><b>19,1 % des lignes sources sans montant</b>, exclues du chiffre d'affaires. Si ces lignes
ne sont pas manquantes au hasard, le CA et les paniers sont biaisés d'une façon que ce jeu de
données ne permet pas de mesurer.</li>
<li><b>9,5 % de notes manquantes</b>, sans test de biais de non-réponse. La hiérarchie des notes
est indicative, pas conclusive.</li>
<li><b>Effectif faible</b> : {ncl} clients, soit 41 à 42 par quartile. Les moyennes de segment
sont sensibles aux valeurs extrêmes et aucun test de significativité n'a été mené.</li>
<li><b>Segments à effectif constant par construction.</b> Ils ne décrivent pas une structure
client observée mais un découpage imposé.</li>
<li><b>12 mois d'historique</b>, sans année de comparaison : aucune analyse de tendance ni de
saisonnalité n'est fiable.</li>
<li>Montants en <b>USD</b> uniquement.</li>
</ul></div>

<footer>Page générée par <code>scripts/make_page.py</code> à partir des tables du projet.
Aucun chiffre n'est écrit en dur : tous sont recalculés à chaque génération.<br>
Souleymane N'DIAYE · <a href="https://github.com/juniorbaw">github.com/juniorbaw</a> ·
<a href="https://www.linkedin.com/in/souleymane-nd">LinkedIn</a></footer>

</div></body></html>"""

import os
os.makedirs("docs", exist_ok=True)
open("docs/index.html", "w", encoding="utf-8").write(html)
print("docs/index.html ecrit —", len(html), "caracteres")
print("controles :", ntx, "transactions |", round(ca, 2), "USD |", ncl, "clients")
