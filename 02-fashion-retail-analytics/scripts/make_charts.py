"""
Génère les graphiques du projet en PNG, aux couleurs de l'identité visuelle.
Usage : python scripts/make_charts.py
Sortie : assets/*.png — régénérables par commande, aucune capture d'écran manuelle.
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

D, OUT = "data/processed/", "assets/"

PLUM, CREAM, WINE, TERRA, SAND, INK, MUTED = (
    "#4A2B3D", "#F5EDE4", "#7B2D3B", "#C4715A", "#E0A48A", "#2B1A24", "#8A7580")
SEG = {"4. VIP": WINE, "3. Fidèle": TERRA, "2. Régulier": SAND, "1. Occasionnel": MUTED}

plt.rcParams.update({
    "figure.facecolor": CREAM, "axes.facecolor": CREAM, "savefig.facecolor": CREAM,
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#D8C9BC", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#E5D9CE", "grid.linewidth": 0.8,
})
usd = FuncFormatter(lambda v, p: ("$%0.0f" % v).replace("$", "$ ") if v >= 1000 else "$%0.0f" % v)
usd = FuncFormatter(lambda v, p: "$" + format(int(v), ",").replace(",", " "))

def titre(ax, msg, sous=None):
    ax.set_title(msg, fontsize=14, fontweight="bold", loc="left", pad=18 if sous else 10)
    if sous:
        ax.text(0, 1.025, sous, transform=ax.transAxes, fontsize=9.5, color=MUTED, va="bottom")

def note(fig, txt, width=125):
    import textwrap
    fig.text(0.012, 0.006, "\n".join(textwrap.wrap(txt, width)),
             fontsize=8, color=MUTED, ha="left", va="bottom")

fct = pd.read_csv(D + "fct_transactions.csv", parse_dates=["date"])
dim = pd.read_csv(D + "dim_clients.csv")
LIM = ("Données synthétiques, montants en USD. 2 750 transactions retenues sur 3 400 — "
       "19,1 % des lignes sources sans montant.")
ORDER = ["4. VIP", "3. Fidèle", "2. Régulier", "1. Occasionnel"]

# 1. Clients vs CA
seg = dim.groupby("segment_valeur").agg(clients=("client_id", "size"), ca=("ca_client", "sum")).reindex(ORDER)
pc, pca = seg.clients / seg.clients.sum() * 100, seg.ca / seg.ca.sum() * 100
fig, ax = plt.subplots(figsize=(9, 4.2))
y, left = np.arange(2), np.zeros(2)
for s in ORDER:
    vals = np.array([pc[s], pca[s]])
    ax.barh(y, vals, left=left, color=SEG[s], height=.5, edgecolor=CREAM, linewidth=2)
    for i, v in enumerate(vals):
        if v > 6:
            ax.text(left[i] + v / 2, y[i], "%.1f %%" % v, ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")
    left += vals
ax.set_yticks(y, ["Part des clients", "Part du chiffre d'affaires"], fontsize=11)
ax.set_xlim(0, 100); ax.set_xticks([]); ax.grid(False); ax.invert_yaxis()
ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
titre(ax, "Un quart des clients, la moitié du chiffre d'affaires",
      "Segments = quartiles de valeur. Les parts de clients sont égales par construction.")
ax.legend([plt.Rectangle((0, 0), 1, 1, color=SEG[s]) for s in ORDER], ORDER,
          loc="lower center", bbox_to_anchor=(.5, -.3), ncol=4, frameon=False, fontsize=9.5)
note(fig, LIM); fig.tight_layout(rect=[0, .06, 1, 1])
fig.savefig(OUT + "01_segments_part.png", dpi=200); plt.close(fig)

# 2. Panier vs fréquence
sm = dim.groupby("segment_valeur").agg(panier=("panier_moyen", "mean"), achats=("nb_achats", "sum")).reindex(ORDER[::-1])
fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
for ax, col, lab, pref in [(axes[0], "achats", "Nombre d'achats", ""), (axes[1], "panier", "Panier moyen (USD)", "$")]:
    b = ax.bar(range(4), sm[col], color=[SEG[s] for s in sm.index], width=.62)
    ax.set_xticks(range(4), [s.split(". ")[1] for s in sm.index], fontsize=10)
    ax.set_ylabel(lab, fontsize=10); ax.grid(axis="x", visible=False)
    for r, v in zip(b, sm[col]):
        ax.text(r.get_x() + r.get_width() / 2, v, pref + format(int(round(v)), ",").replace(",", " "),
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylim(0, sm[col].max() * 1.2)
axes[0].set_title("Fréquence : les VIP n'achètent pas plus", fontsize=11.5, fontweight="bold", loc="left")
axes[1].set_title("Panier : ils achètent 2,7x plus cher", fontsize=11.5, fontweight="bold", loc="left")
fig.suptitle("Le levier des VIP est le panier, pas la fréquence", fontsize=14, fontweight="bold", x=.012, ha="left", y=.985)
note(fig, LIM + "  Échelles distinctes : deux panneaux plutôt qu'un double axe vertical.")
fig.tight_layout(rect=[0, .075, 1, .92]); fig.savefig(OUT + "02_panier_vs_frequence.png", dpi=200); plt.close(fig)

# 3. CA x satisfaction
prod = fct.groupby("article").agg(ca=("montant", "sum"), note_moy=("note", "mean"), n=("montant", "size")).reset_index().dropna()
fig, ax = plt.subplots(figsize=(9.5, 5.2))
al = prod.note_moy < 2.70
ax.scatter(prod.ca[~al], prod.note_moy[~al], s=48, color=MUTED, alpha=.7, zorder=3)
ax.scatter(prod.ca[al], prod.note_moy[al], s=95, color=WINE, zorder=4)
ax.axhline(2.70, color=TERRA, ls="--", lw=1.4, zorder=2)
ax.text(prod.ca.max(), 2.715, "seuil d'alerte 2,70", ha="right", va="bottom", fontsize=9, color=TERRA)
ax.set_xlim(prod.ca.min() * .82, prod.ca.max() * 1.10)
ax.set_ylim(prod.note_moy.min() - .12, prod.note_moy.max() + .10)
for _, r in prod[al].iterrows():
    droite = r.ca < prod.ca.max() * .75
    ax.annotate(r.article, (r.ca, r.note_moy),
                xytext=(9 if droite else -9, -3), textcoords="offset points",
                ha="left" if droite else "right", va="center",
                fontsize=9.5, fontweight="bold", color=WINE)
ax.xaxis.set_major_formatter(usd)
ax.set_xlabel("Chiffre d'affaires par article", fontsize=10); ax.set_ylabel("Note moyenne sur 5", fontsize=10)
titre(ax, "Le premier contributeur au chiffre d'affaires est le plus mal noté",
      "50 articles. En rouge, les 5 articles sous le seuil d'alerte de 2,70 / 5.")
note(fig, LIM + "  9,5 % de notes manquantes, aucun test de biais de non-réponse.")
fig.tight_layout(rect=[0, .07, 1, 1]); fig.savefig(OUT + "03_ca_satisfaction.png", dpi=200); plt.close(fig)

# 4. Nuage clients
fig, ax = plt.subplots(figsize=(9.5, 5.2))
for s in ORDER[::-1]:
    d = dim[dim.segment_valeur == s]
    ax.scatter(d.ca_client, d.nb_achats, s=d.panier_moyen * .55, color=SEG[s],
               alpha=.82, label=s, edgecolor="white", linewidth=.6)
ax.xaxis.set_major_formatter(usd)
ax.set_xlabel("Chiffre d'affaires du client", fontsize=10); ax.set_ylabel("Nombre d'achats", fontsize=10)
titre(ax, "Les VIP s'étirent vers la droite, pas vers le haut",
      "166 clients. Taille du point = panier moyen du client.")
ax.legend(frameon=False, fontsize=9.5, loc="upper left")
note(fig, LIM + "  41 à 42 clients par quartile : moyennes sensibles aux valeurs extrêmes.")
fig.tight_layout(rect=[0, .07, 1, 1]); fig.savefig(OUT + "04_clients_nuage.png", dpi=200); plt.close(fig)

# 5. Top articles
top = prod.nlargest(10, "ca").sort_values("ca")
fig, ax = plt.subplots(figsize=(9, 4.6))
b = ax.barh(top.article, top.ca, color=[WINE if a < 2.70 else TERRA for a in top.note_moy], height=.68)
for r, v in zip(b, top.ca):
    ax.text(v - top.ca.max() * .013, r.get_y() + r.get_height() / 2, "$" + format(int(v), ",").replace(",", " "),
            ha="right", va="center", color="white", fontsize=9.5, fontweight="bold")
ax.xaxis.set_major_formatter(usd); ax.grid(axis="y", visible=False)
titre(ax, "Tunic domine le chiffre d'affaires — et déçoit",
      "Top 10 des articles. En rouge foncé, note moyenne sous 2,70 / 5.")
note(fig, LIM); fig.tight_layout(rect=[0, .035, 1, 1])
fig.savefig(OUT + "05_top_articles.png", dpi=200); plt.close(fig)

print("5 graphiques ecrits dans", OUT)
print("controle CA          :", round(fct.montant.sum(), 2))
print("controle transactions:", len(fct))
print("controle clients     :", len(dim))
